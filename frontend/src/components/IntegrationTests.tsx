'use client';

import { useState, useEffect } from 'react';
import { useAccount } from '@starknet-react/core';
import { useStrategyRouter } from '@/hooks/useStrategyRouter';
import { getConfig } from '@/lib/config';
import { Call, RpcProvider, Contract, uint256 } from 'starknet';
import { useProofHistory } from '@/hooks/useProofHistory';
import { ProofBadge } from './ProofBadge';

// Strategy Router V3.5 ABI including all functions and MIST integration
const STRATEGY_ROUTER_V35_ABI = [
  {
    name: 'deposit',
    type: 'function',
    inputs: [{ name: 'amount', type: 'core::integer::u256' }],
    outputs: [],
    state_mutability: 'external',
  },
  {
    name: 'withdraw',
    type: 'function',
    inputs: [{ name: 'amount', type: 'core::integer::u256' }],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'external',
  },
  {
    name: 'get_user_balance',
    type: 'function',
    inputs: [{ name: 'user', type: 'core::starknet::contract_address::ContractAddress' }],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_total_value_locked',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_allocation',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }, { type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_total_yield_accrued',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_protocol_tvl',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }, { type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_jediswap_tvl',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'get_ekubo_tvl',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::integer::u256' }],
    state_mutability: 'view',
  },
  {
    name: 'deploy_to_protocols',
    type: 'function',
    inputs: [],
    outputs: [],
    state_mutability: 'external',
  },
  {
    name: 'test_jediswap_only',
    type: 'function',
    inputs: [{ name: 'amount', type: 'core::integer::u256' }],
    outputs: [],
    state_mutability: 'external',
  },
  {
    name: 'test_ekubo_only',
    type: 'function',
    inputs: [{ name: 'amount', type: 'core::integer::u256' }],
    outputs: [],
    state_mutability: 'external',
  },
  // MIST.cash Privacy Integration Functions
  {
    name: 'commit_mist_deposit',
    type: 'function',
    inputs: [
      { name: 'commitment_hash', type: 'core::felt252' },
      { name: 'expected_amount', type: 'core::integer::u256' },
    ],
    outputs: [],
    state_mutability: 'external',
  },
  {
    name: 'reveal_and_claim_mist_deposit',
    type: 'function',
    inputs: [{ name: 'secret', type: 'core::felt252' }],
    outputs: [
      { type: 'core::starknet::contract_address::ContractAddress' },
      { type: 'core::integer::u256' },
    ],
    state_mutability: 'external',
  },
  {
    name: 'get_mist_commitment',
    type: 'function',
    inputs: [{ name: 'commitment_hash', type: 'core::felt252' }],
    outputs: [
      { type: 'core::starknet::contract_address::ContractAddress' },
      { type: 'core::integer::u256' },
      { type: 'core::bool' },
    ],
    state_mutability: 'view',
  },
  {
    name: 'set_mist_chamber',
    type: 'function',
    inputs: [{ name: 'chamber', type: 'core::starknet::contract_address::ContractAddress' }],
    outputs: [],
    state_mutability: 'external',
  },
  {
    name: 'get_mist_chamber',
    type: 'function',
    inputs: [],
    outputs: [{ type: 'core::starknet::contract_address::ContractAddress' }],
    state_mutability: 'view',
  },
];

interface IntegrationChecklistItem {
  id: string;
  category: string;
  name: string;
  status: 'completed' | 'in_progress' | 'blocked' | 'planned';
  description: string;
  testFunction?: string;
  notes?: string;
}

export function IntegrationTests() {
  const { address, account } = useAccount();
  const router = useStrategyRouter();
  const proofHistory = useProofHistory(5);
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [devLog, setDevLog] = useState<string>('');
  const [devLogLoading, setDevLogLoading] = useState(true);
  const [useOwnerWallet, setUseOwnerWallet] = useState(false);
  const [depositing, setDepositing] = useState(false);
  const [totalYield, setTotalYield] = useState<string>('0');
  const [yieldLoading, setYieldLoading] = useState(false);
  const [protocolStats, setProtocolStats] = useState<{
    jediswap: { tvl: string; apy: string };
    ekubo: { tvl: string; apy: string };
  }>({
    jediswap: { tvl: '0', apy: '0' },
    ekubo: { tvl: '0', apy: '0' },
  });
  const [statsLoading, setStatsLoading] = useState(false);

  const config = getConfig();
  const contractAddress = config.strategyRouterAddress;
  const STRK_TOKEN_ADDRESS = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d';
  
  // Functions that require owner access
  const ownerOnlyFunctions = ['deploy_to_protocols', 'test_jediswap_only', 'test_ekubo_only', 'accrue_yields', 'accrue_jediswap_yields', 'accrue_ekubo_yields', 'recall_from_protocols'];

  // Simple deposit function for test actions
  const handleDeposit = async () => {
    if (!account || !address) {
      alert('Please connect your wallet');
      return;
    }
    
    setDepositing(true);
    try {
      const provider = new RpcProvider({ nodeUrl: config.rpcUrl });
      
      // Small test deposit: 0.01 STRK
      const testAmount = BigInt('10000000000000000'); // 0.01 STRK
      const amountU256 = uint256.bnToUint256(testAmount);
      
      // First approve STRK spending
      const approveCall: Call = {
        contractAddress: STRK_TOKEN_ADDRESS,
        entrypoint: 'approve',
        calldata: [contractAddress, amountU256.low.toString(), amountU256.high.toString()],
      };
      
      const approveResult = await account.execute(approveCall);
      console.log('Approval tx:', approveResult.transaction_hash);
      
      // Wait for approval confirmation
      await provider.waitForTransaction(approveResult.transaction_hash, { retryInterval: 2000 });
      
      // Then deposit
      const depositCall: Call = {
        contractAddress: contractAddress,
        entrypoint: 'deposit',
        calldata: [amountU256.low.toString(), amountU256.high.toString()],
      };
      
      const depositResult = await account.execute(depositCall);
      await provider.waitForTransaction(depositResult.transaction_hash, { retryInterval: 2000 });
      
      alert(`✅ Test deposit successful! Transaction: ${depositResult.transaction_hash}\n\nYou can now test deploy_to_protocols.`);
    } catch (error: any) {
      alert(`❌ Deposit failed: ${error.message}`);
    } finally {
      setDepositing(false);
    }
  };

  // Fetch dev log on component mount
  // Fetch total yield accrued
  const fetchYield = async () => {
    if (!contractAddress) return;
    
    setYieldLoading(true);
    try {
      const provider = new RpcProvider({ nodeUrl: config.rpcUrl });
      const contract = new Contract(STRATEGY_ROUTER_V35_ABI, contractAddress, provider);
      const result = await contract.call('get_total_yield_accrued', []);
      // Handle both U256 format and direct bigint
      let yieldAmount: bigint;
      if (typeof result === 'bigint') {
        yieldAmount = result;
      } else if (result && typeof result === 'object' && 'low' in result && 'high' in result) {
        yieldAmount = uint256.uint256ToBN(result as any);
      } else {
        yieldAmount = BigInt(String(result));
      }
      const yieldStrk = (Number(yieldAmount) / 1e18).toFixed(6);
      setTotalYield(yieldStrk);
    } catch (error) {
      console.error('Error fetching yield:', error);
      setTotalYield('Error');
    } finally {
      setYieldLoading(false);
    }
  };

  // Fetch protocol statistics (TVL, APY)
  const fetchProtocolStats = async () => {
    if (!contractAddress) {
      console.warn('No contract address available for TVL fetch');
      setProtocolStats({
        jediswap: { tvl: 'N/A', apy: 'N/A' },
        ekubo: { tvl: 'N/A', apy: 'N/A' },
      });
      return;
    }
    
    setStatsLoading(true);
    try {
      const provider = new RpcProvider({ nodeUrl: config.rpcUrl });
      const contract = new Contract(STRATEGY_ROUTER_V35_ABI, contractAddress, provider);
      
      // Helper to check if error indicates missing function
      const isFunctionNotFound = (error: any): boolean => {
        const msg = error?.message || String(error || '');
        return msg.includes('Contract not found') || 
               msg.includes('ENTRYPOINT_NOT_FOUND') ||
               msg.includes('Entry point') ||
               msg.includes('undefined');
      };
      
      // Parse TVL values
      const parseU256 = (result: any): bigint => {
        if (typeof result === 'bigint') return result;
        if (result && typeof result === 'object' && 'low' in result && 'high' in result) {
          return uint256.uint256ToBN(result as any);
        }
        if (Array.isArray(result) && result.length > 0) {
          // Handle array response (e.g., from get_protocol_tvl)
          const first = result[0];
          if (typeof first === 'bigint') return first;
          if (first && typeof first === 'object' && 'low' in first && 'high' in first) {
            return uint256.uint256ToBN(first as any);
          }
          return BigInt(String(first));
        }
        return BigInt(String(result || '0'));
      };
      
      // Try v3 functions first (get_protocol_tvl or individual get_jediswap_tvl/get_ekubo_tvl)
      let jediTvl: bigint, ekuboTvl: bigint;
      let tvlFunctionsAvailable = false;
      let isV3Contract = false;
      
      try {
        // Try v3's get_protocol_tvl first (most efficient - returns both in one call)
        const protocolTvlResult = await contract.call('get_protocol_tvl', []);
        console.log('✅ get_protocol_tvl successful (v3 contract detected):', protocolTvlResult);
        tvlFunctionsAvailable = true;
        isV3Contract = true;
        
        // get_protocol_tvl returns [jediswap_tvl, ekubo_tvl]
        if (Array.isArray(protocolTvlResult) && protocolTvlResult.length >= 2) {
          jediTvl = parseU256(protocolTvlResult[0]);
          ekuboTvl = parseU256(protocolTvlResult[1]);
        } else {
          throw new Error('Unexpected get_protocol_tvl response format');
        }
      } catch (protocolTvlError: any) {
        if (isFunctionNotFound(protocolTvlError)) {
          console.log('ℹ️ get_protocol_tvl not found, trying individual v3 calls...');
        } else {
          console.warn('⚠️ get_protocol_tvl failed, trying individual calls:', protocolTvlError.message);
        }
        
        // Fallback to individual v3 calls
        const [jediTvlResult, ekuboTvlResult] = await Promise.all([
          contract.call('get_jediswap_tvl', []).catch((e: any) => {
            if (isFunctionNotFound(e)) {
              return null; // Will try v2 approach
            } else {
              console.error('❌ get_jediswap_tvl failed:', e.message || e);
              return null;
            }
          }),
          contract.call('get_ekubo_tvl', []).catch((e: any) => {
            if (isFunctionNotFound(e)) {
              return null; // Will try v2 approach
            } else {
              console.error('❌ get_ekubo_tvl failed:', e.message || e);
              return null;
            }
          }),
        ]);
        
        if (jediTvlResult && ekuboTvlResult) {
          // v3 contract with individual functions
          console.log('✅ Individual v3 TVL functions available');
          tvlFunctionsAvailable = true;
          isV3Contract = true;
          jediTvl = parseU256(jediTvlResult);
          ekuboTvl = parseU256(ekuboTvlResult);
        } else {
          // v2 contract - use get_total_value_locked and split by allocation
          console.log('ℹ️ v3 TVL functions not found, trying v2 approach (get_total_value_locked + allocation)...');
          
          try {
            // Get total TVL from v2 contract
            const totalTvlResult = await contract.call('get_total_value_locked', []);
            const totalTvl = parseU256(totalTvlResult);
            
            // Get allocation to split the TVL
            const allocationResult = await contract.call('get_allocation', []);
            let jediAllocBps = 5000n; // Default 50%
            let ekuboAllocBps = 5000n; // Default 50%
            
            if (Array.isArray(allocationResult) && allocationResult.length >= 2) {
              jediAllocBps = parseU256(allocationResult[0]);
              ekuboAllocBps = parseU256(allocationResult[1]);
            } else if (typeof allocationResult === 'object' && allocationResult !== null) {
              // Handle object format
              const alloc = allocationResult as any;
              if ('low' in alloc && 'high' in alloc) {
                jediAllocBps = parseU256(alloc);
                ekuboAllocBps = 10000n - jediAllocBps; // Assume they sum to 10000 (100%)
              }
            }
            
            // Split total TVL by allocation (basis points: 10000 = 100%)
            // jediTvl = totalTvl * jediAllocBps / 10000
            jediTvl = (totalTvl * jediAllocBps) / 10000n;
            ekuboTvl = (totalTvl * ekuboAllocBps) / 10000n;
            
            tvlFunctionsAvailable = true;
            isV3Contract = false;
            console.log(`✅ v2 contract: Total TVL ${totalTvl.toString()}, split ${jediAllocBps.toString()}/${ekuboAllocBps.toString()} bps`);
          } catch (v2Error: any) {
            console.error('❌ v2 approach also failed:', v2Error.message);
            tvlFunctionsAvailable = false;
            jediTvl = 0n;
            ekuboTvl = 0n;
          }
        }
      }
      
      // Fetch total yield
      let totalYield = 0n;
      let yieldFunctionAvailable = false;
      try {
        const totalYieldResult = await contract.call('get_total_yield_accrued', []);
        totalYield = parseU256(totalYieldResult);
        yieldFunctionAvailable = true;
      } catch (yieldError: any) {
        if (isFunctionNotFound(yieldError)) {
          console.warn('⚠️ get_total_yield_accrued not found on contract');
        } else {
          console.warn('⚠️ get_total_yield_accrued failed:', yieldError.message);
        }
      }
      
      // If TVL functions are not available at all, show "Not Supported"
      if (!tvlFunctionsAvailable) {
        console.warn(`⚠️ Contract at ${contractAddress} does not support TVL functions. This may be an older contract version.`);
        setProtocolStats({
          jediswap: { tvl: 'Not Supported', apy: 'N/A' },
          ekubo: { tvl: 'Not Supported', apy: 'N/A' },
        });
        return;
      }
      
      // Log which contract version we detected
      if (isV3Contract) {
        console.log('📊 Using v3 contract TVL functions');
      } else {
        console.log('📊 Using v2 contract (total TVL split by allocation)');
      }
      
      const jediTvlStrk = Number(jediTvl) / 1e18;
      const ekuboTvlStrk = Number(ekuboTvl) / 1e18;
      const totalYieldStrk = Number(totalYield) / 1e18;
      const totalTvl = jediTvlStrk + ekuboTvlStrk;
      
      console.log('📊 TVL Stats:', {
        jediTvl: jediTvlStrk,
        ekuboTvl: ekuboTvlStrk,
        totalTvl,
        totalYield: totalYieldStrk,
      });
      
      // Calculate APY (simplified: yield as % of TVL, annualized)
      // This is a rough estimate - in production you'd track yield over time
      let jediApy = '0.00';
      let ekuboApy = '0.00';
      
      if (yieldFunctionAvailable && totalTvl > 0) {
        if (jediTvlStrk > 0) {
          // APY = (yield allocated to protocol / TVL) * 100
          const jediYield = totalYieldStrk * (jediTvlStrk / totalTvl);
          jediApy = ((jediYield / jediTvlStrk) * 100).toFixed(2);
        }
        if (ekuboTvlStrk > 0) {
          const ekuboYield = totalYieldStrk * (ekuboTvlStrk / totalTvl);
          ekuboApy = ((ekuboYield / ekuboTvlStrk) * 100).toFixed(2);
        }
      } else if (!yieldFunctionAvailable) {
        // If yield function not available, show N/A
        jediApy = 'N/A';
        ekuboApy = 'N/A';
      }
      
      setProtocolStats({
        jediswap: {
          tvl: jediTvlStrk.toFixed(4),
          apy: jediApy,
        },
        ekubo: {
          tvl: ekuboTvlStrk.toFixed(4),
          apy: ekuboApy,
        },
      });
    } catch (error: any) {
      console.error('❌ Error fetching protocol stats (outer catch):', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        contractAddress,
        rpcUrl: config.rpcUrl,
      });
      
      // Check if it's a contract not found error
      const isContractNotFound = error?.message?.includes('Contract not found') || 
                                 error?.message?.includes('undefined');
      
      if (isContractNotFound) {
        console.warn(`⚠️ Contract at ${contractAddress} may not be deployed or address is incorrect.`);
        setProtocolStats({
          jediswap: { tvl: 'Contract Not Found', apy: 'N/A' },
          ekubo: { tvl: 'Contract Not Found', apy: 'N/A' },
        });
      } else {
        setProtocolStats({
          jediswap: { tvl: 'Error', apy: 'Error' },
          ekubo: { tvl: 'Error', apy: 'Error' },
        });
      }
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    fetch('/api/integration-tests/dev-log')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setDevLog(data.content);
        } else {
          setDevLog('# Integration Tests Development Log\n\nError loading log file.');
        }
        setDevLogLoading(false);
      })
      .catch(error => {
        console.error('Error fetching dev log:', error);
        setDevLog('# Integration Tests Development Log\n\nError loading log file.');
        setDevLogLoading(false);
      });
    
    // Fetch yield and protocol stats on mount
    fetchYield();
    fetchProtocolStats();
  }, [contractAddress]);

  const checklist: IntegrationChecklistItem[] = [
    // Core Functionality
    {
      id: 'deposit',
      category: 'Core',
      name: 'STRK Deposit',
      status: 'completed',
      description: 'Users can deposit STRK to the Strategy Router',
      testFunction: 'deposit',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'withdraw',
      category: 'Core',
      name: 'STRK Withdrawal',
      status: 'completed',
      description: 'Users can withdraw STRK from the Strategy Router',
      testFunction: 'withdraw',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'balance_tracking',
      category: 'Core',
      name: 'Balance Tracking',
      status: 'completed',
      description: 'Contract tracks user balances correctly',
      testFunction: 'get_user_balance',
      notes: '✅ Functional - Tested. Active for future testing.'
    },

    // JediSwap Integration
    {
      id: 'jediswap_router_swap',
      category: 'JediSwap',
      name: 'JediSwap V2 Router - Swap',
      status: 'completed',
      description: 'Swap STRK to ETH using JediSwap V2 Router exact_input_single()',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'jediswap_nft_mint',
      category: 'JediSwap',
      name: 'JediSwap NFT Position Manager - Mint',
      status: 'completed',
      description: 'Add liquidity via NFT Position Manager mint() with I32 ticks',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'jediswap_full_integration',
      category: 'JediSwap',
      name: 'JediSwap Full Integration',
      status: 'completed',
      description: 'Complete flow: Swap + Add Liquidity + Track Position',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },

    // Ekubo Integration
    {
      id: 'ekubo_positions_mint',
      category: 'Ekubo',
      name: 'Ekubo Positions - Mint & Deposit',
      status: 'completed',
      description: 'Add liquidity via Ekubo Positions mint_and_deposit()',
      testFunction: 'test_ekubo_only',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'ekubo_swap',
      category: 'Ekubo',
      name: 'Ekubo - Swap STRK to ETH',
      status: 'completed',
      description: 'Swap STRK to ETH before adding liquidity (uses JediSwap router)',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'ekubo_full_integration',
      category: 'Ekubo',
      name: 'Ekubo Full Integration',
      status: 'completed',
      description: 'Complete flow: Swap + Add Liquidity + Track Position',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },

    // Protocol Deployment
    {
      id: 'deploy_both_protocols',
      category: 'Deployment',
      name: 'Deploy to Both Protocols',
      status: 'completed',
      description: 'deploy_to_protocols() - Deploy pending deposits to JediSwap and Ekubo (⚠️ Requires deposits first - use Deposit in main dashboard)',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Functional - Tested frontend and backend. Active for future testing.'
    },
    {
      id: 'allocation_management',
      category: 'Deployment',
      name: 'Allocation Management',
      status: 'completed',
      description: 'Update allocation percentages between protocols',
      testFunction: 'get_allocation',
      notes: '✅ Functional - Tested. Active for future testing.'
    },

    // Advanced Features
    {
      id: 'position_tracking',
      category: 'Advanced',
      name: 'Position Tracking',
      status: 'in_progress',
      description: 'Query NFT position IDs and counts from JediSwap and Ekubo',
      testFunction: 'get_position_counts',
      notes: 'Query functions available - get_jediswap_position_count, get_ekubo_position_count'
    },
    {
      id: 'yield_accrual',
      category: 'Advanced',
      name: 'Yield Accrual (Both Protocols)',
      status: 'in_progress',
      description: 'Accrue yields from liquidity positions (collect fees from both protocols)',
      testFunction: 'accrue_yields',
      notes: 'Owner-only function - collects fees from both protocols'
    },
    {
      id: 'yield_accrual_jediswap',
      category: 'Advanced',
      name: 'Yield Accrual - JediSwap Only',
      status: 'in_progress',
      description: 'Accrue yields from JediSwap liquidity positions only',
      testFunction: 'accrue_jediswap_yields',
      notes: 'Owner-only function - collects fees from JediSwap positions'
    },
    {
      id: 'yield_accrual_ekubo',
      category: 'Advanced',
      name: 'Yield Accrual - Ekubo Only',
      status: 'in_progress',
      description: 'Accrue yields from Ekubo liquidity positions only',
      testFunction: 'accrue_ekubo_yields',
      notes: 'Owner-only function - collects fees from Ekubo positions'
    },
    {
      id: 'rebalancing',
      category: 'Advanced',
      name: 'Rebalancing',
      status: 'in_progress',
      description: 'Rebalance positions based on allocation changes',
      testFunction: 'rebalance',
      notes: 'Function exists - needs testing'
    },
    {
      id: 'recall_from_protocols',
      category: 'Advanced',
      name: 'Recall from Protocols',
      status: 'in_progress',
      description: 'Withdraw liquidity from JediSwap/Ekubo positions and return to contract',
      testFunction: 'recall_from_protocols',
      notes: 'Owner-only function - withdraws liquidity from protocols. Requires position index and liquidity amount.'
    },
    {
      id: 'slippage_protection',
      category: 'Advanced',
      name: 'Slippage Protection',
      status: 'planned',
      description: 'Add slippage protection for swaps and liquidity provision',
      notes: 'Currently set to 0 (no protection) - requires contract modification'
    },
    
    // MIST.cash Privacy Integration (Testing Only)
    {
      id: 'mist_commit_deposit',
      category: 'Privacy',
      name: 'MIST: Commit Deposit (Hash)',
      status: 'planned',
      description: 'Commit to MIST deposit by sending hash(secret) to router',
      testFunction: 'commit_mist_deposit',
      notes: 'Pattern 2 Phase 1: User commits hash, router stores commitment. Testing only - not in main UI.'
    },
    {
      id: 'mist_reveal_claim',
      category: 'Privacy',
      name: 'MIST: Reveal & Claim',
      status: 'planned',
      description: 'Reveal secret to router, router claims from MIST chamber',
      testFunction: 'reveal_and_claim_mist_deposit',
      notes: 'Pattern 2 Phase 2: User reveals secret when ready, router claims. Testing only - not in main UI.'
    },
    {
      id: 'mist_check_commitment',
      category: 'Privacy',
      name: 'MIST: Check Commitment',
      status: 'planned',
      description: 'Query commitment status before revealing',
      testFunction: 'get_mist_commitment',
      notes: 'View function to check if commitment exists and if revealed. Testing only - not in main UI.'
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-800 bg-green-50 border-green-300';
      case 'in_progress': return 'text-amber-800 bg-amber-50 border-amber-300';
      case 'blocked': return 'text-red-800 bg-red-50 border-red-300';
      case 'planned': return 'text-slate-700 bg-slate-50 border-slate-300';
      default: return 'text-slate-700 bg-slate-50 border-slate-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'in_progress': return '🔄';
      case 'blocked': return '❌';
      case 'planned': return '📋';
      default: return '❓';
    }
  };

  const handleTest = async (item: IntegrationChecklistItem) => {
    if (!item.testFunction || !contractAddress) {
      alert('Test function not available');
      return;
    }

    // Check if this is an owner-only function
    const isOwnerOnly = ownerOnlyFunctions.includes(item.testFunction);
    const shouldUseOwnerWallet = useOwnerWallet && isOwnerOnly;

    // For owner-only functions, require either owner wallet mode or user's wallet to be owner
    if (isOwnerOnly && !shouldUseOwnerWallet) {
      if (!account || !address) {
        alert('Wallet not connected. Please connect your wallet or use Owner Wallet mode.');
        return;
      }
      // We'll let the transaction fail with Unauthorized if user isn't owner
      // The error handler will show a helpful message
    } else if (!shouldUseOwnerWallet && (!account || !address)) {
      alert('Wallet not connected');
      return;
    }

    setTesting(item.id);
    setTestResults(prev => ({ ...prev, [item.id]: { status: 'testing', message: 'Preparing transaction...' } }));

    try {
      // Create provider once for reuse
      const provider = new RpcProvider({ nodeUrl: config.rpcUrl });
      
      // If using owner wallet, route through API
      if (shouldUseOwnerWallet) {
        // For API calls, we need to send the raw function arguments (not the populated calldata)
        // The API will handle the population
        let calldata: any[] = [];
        if (item.testFunction === 'deploy_to_protocols') {
          calldata = []; // No arguments
        } else if (item.testFunction === 'test_jediswap_only') {
          // Send the amount as a string (BigInt can't be JSON serialized)
          const amount = '100000000000000000';
          calldata = [amount];
        } else if (item.testFunction === 'test_ekubo_only') {
          // Send the amount as a string (BigInt can't be JSON serialized)
          const amount = '100000000000000000';
          calldata = [amount];
        } else if (item.testFunction === 'accrue_yields' || item.testFunction === 'accrue_jediswap_yields' || item.testFunction === 'accrue_ekubo_yields') {
          calldata = []; // No arguments
        } else if (item.testFunction === 'rebalance') {
          calldata = []; // No arguments
        }

        // Call backend API to execute as owner
        console.log('[Frontend] Sending to API:', { functionName: item.testFunction, calldata });
        let response;
        try {
          response = await fetch('/api/integration-tests/execute-as-owner', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              functionName: item.testFunction,
              calldata: calldata || [],
            }),
          });
        } catch (fetchError: any) {
          throw new Error(`Failed to reach API route: ${fetchError.message}\n\n` +
            `💡 This might mean:\n` +
            `- The API route is not deployed on this server\n` +
            `- The server needs to be restarted\n` +
            `- Check if you're on the correct domain (dev vs prod)`);
        }

        let data: any;
        try {
          data = await response.json();
        } catch (e) {
          // If response isn't JSON, try to get text
          const errorText = await response.text();
          throw new Error(`API returned ${response.status}: ${errorText}`);
        }
        
        console.log('[Frontend] API response:', data);
        
        // Even if API returns error, check if we have a transaction hash
        // Transaction might have succeeded even if API route failed (e.g., receipt waiting timeout)
        if (data.transactionHash) {
          console.log('[Frontend] ⚠️ API returned error but transaction hash exists:', data.transactionHash);
          console.log('[Frontend] Transaction may have succeeded - will verify on-chain');
          
          // Set pending state and verify transaction on-chain
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'pending',
              message: 'Transaction submitted (API error, verifying on-chain)...',
              txHash: data.transactionHash,
              timestamp: new Date().toISOString(),
              viaOwnerWallet: true,
            }
          }));
          
          // Verify transaction on-chain
          try {
            const receipt = await provider.waitForTransaction(data.transactionHash, { retryInterval: 2000 });
            
            // Extract gas fee
            let gasFeeWei = BigInt(0);
            const actualFee = (receipt as any).actual_fee;
            if (actualFee) {
              try {
                if (typeof actualFee === 'string') {
                  gasFeeWei = BigInt(actualFee);
                } else if (actualFee && typeof actualFee === 'object') {
                  // Handle new format: { amount: string; unit: "WEI" | "FRI" }
                  if (actualFee.amount !== undefined) {
                    gasFeeWei = BigInt(actualFee.amount);
                  } else if (actualFee.low !== undefined && actualFee.high !== undefined) {
                    // Handle old U256 format: { low: string, high: string }
                    const low = BigInt(actualFee.low || '0');
                    const high = BigInt(actualFee.high || '0');
                    gasFeeWei = low + (high << 128n);
                  }
                }
              } catch (e) {
                console.warn('Could not parse gas fee:', e);
              }
            }
            
            const gasFeeEth = Number(gasFeeWei) / 1e18;
            const finalityStatus = (receipt as any).finality_status;
            const executionStatus = (receipt as any).execution_status;
            const isSuccess = (finalityStatus === 'ACCEPTED_ON_L2' || finalityStatus === 'ACCEPTED_ON_L1') && 
                             executionStatus === 'SUCCEEDED';
            
            setTestResults(prev => ({
              ...prev,
              [item.id]: {
                status: isSuccess ? 'success' : 'error',
                message: isSuccess 
                  ? `✅ Success! Transaction confirmed on-chain. Gas: ${gasFeeEth.toFixed(6)} ETH`
                  : `Transaction ${finalityStatus || 'unknown'}`,
                txHash: data.transactionHash,
                gasFee: gasFeeEth.toFixed(6),
                timestamp: new Date().toISOString(),
                viaOwnerWallet: true,
              }
            }));
            
            setTesting(null);
            return; // Exit early - transaction verified successfully
          } catch (verifyError: any) {
            console.error('[Frontend] Failed to verify transaction on-chain:', verifyError);
            // Fall through to show the original API error
          }
        }
        
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error(`API route not found (404).\n\n` +
              `💡 The /api/integration-tests/execute-as-owner route may not be deployed.\n` +
              `- On production: This is expected - owner wallet API is disabled for security\n` +
              `- On dev/staging: Restart the Next.js server\n` +
              `- Check server logs for errors`);
          } else if (response.status === 403) {
            throw new Error(data.error || `API route disabled (403).\n\n` +
              `🔒 Security: Owner wallet API is disabled on production.\n` +
              `On production, only the contract owner can execute owner-only functions directly via their wallet.\n` +
              `This is the secure, intended behavior.`);
          }
          // Use user-friendly message if available, otherwise use error
          const errorMsg = data.userMessage || data.error || `API returned ${response.status}`;
          const details = data.details || data.stack || '';
          throw new Error(`${errorMsg}${details && !data.userMessage ? `\n\nDetails: ${details}` : ''}`);
        }
        
        if (!data.success) {
          // Use user-friendly message if available, otherwise use error
          const errorMsg = data.userMessage || data.error || 'Failed to execute as owner';
          const details = data.details || data.stack || '';
          throw new Error(`${errorMsg}${details && !data.userMessage ? `\n\nDetails: ${details}` : ''}`);
        }

        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            status: 'pending',
            message: 'Transaction submitted via owner wallet, waiting for confirmation...',
            txHash: data.transactionHash,
            timestamp: new Date().toISOString(),
            viaOwnerWallet: true,
          }
        }));

        // Wait for transaction receipt
        const receipt = await provider.waitForTransaction(data.transactionHash, { retryInterval: 2000 });
        
        // Extract gas fee
        let gasFeeWei = BigInt(0);
        const actualFee = (receipt as any).actual_fee;
        if (actualFee) {
          try {
            if (typeof actualFee === 'string') {
              gasFeeWei = BigInt(actualFee);
            } else if (actualFee && typeof actualFee === 'object') {
              // Handle new format: { amount: string; unit: "WEI" | "FRI" }
              if (actualFee.amount !== undefined) {
                gasFeeWei = BigInt(actualFee.amount);
              } else if (actualFee.low !== undefined && actualFee.high !== undefined) {
                // Handle old U256 format: { low: string, high: string }
                const low = BigInt(actualFee.low || '0');
                const high = BigInt(actualFee.high || '0');
                gasFeeWei = low + (high << 128n);
              }
            }
          } catch (e) {
            console.warn('Could not parse gas fee:', e);
          }
        }

        const gasFeeEth = Number(gasFeeWei) / 1e18;
        const gasFeeLink = `https://sepolia.voyager.online/tx/${data.transactionHash}`;
        const finalityStatus = (receipt as any).finality_status;
        const executionStatus = (receipt as any).execution_status;
        const isSuccess = (finalityStatus === 'ACCEPTED_ON_L2' || finalityStatus === 'ACCEPTED_ON_L1') && 
                         executionStatus === 'SUCCEEDED';

        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            status: isSuccess ? 'success' : 'error',
            message: isSuccess 
              ? `✅ Success! Executed via owner wallet. Gas: ${gasFeeEth.toFixed(6)} ETH`
              : `Transaction ${finalityStatus || 'unknown'}`,
            txHash: data.transactionHash,
            gasFee: gasFeeEth.toFixed(6),
            gasFeeLink,
            timestamp: new Date().toISOString(),
            viaOwnerWallet: true,
          }
        }));

        setTesting(null);
        return;
      }

      // Regular execution via user's wallet
      // Verify contract is accessible before attempting transaction
      // (provider already created above)
      try {
        // Try to get contract class to verify it exists
        await provider.getClassAt(contractAddress);
      } catch (verifyError: any) {
        const errorMsg = verifyError.message || verifyError.toString();
        if (errorMsg.includes('not found') || errorMsg.includes('not deployed')) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: `Contract not found at ${contractAddress}. It may not be deployed yet or RPC hasn't indexed it. Please verify the contract address and try again.`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
        // If it's a different error, continue - might be a class hash issue but contract exists
        console.warn('Contract verification warning:', verifyError);
      }

      // Manually construct Call objects (don't use populate - it can return undefined values)
      // Use uint256 for u256 conversion
      const calls: Call[] = [];
      
      if (item.testFunction === 'deploy_to_protocols') {
        const call: Call = {
          contractAddress: contractAddress,
          entrypoint: 'deploy_to_protocols',
          calldata: [], // No parameters
        };
        console.log('🔍 deploy_to_protocols call:', {
          contractAddress: call.contractAddress,
          entrypoint: call.entrypoint,
          calldata: call.calldata
        });
        calls.push(call);
      } else if (item.testFunction === 'test_jediswap_only') {
        // Test with 0.1 STRK (100000000000000000 wei)
        const amount = BigInt('100000000000000000');
        const amountU256 = uint256.bnToUint256(amount);
        const call: Call = {
          contractAddress: contractAddress,
          entrypoint: 'test_jediswap_only',
          calldata: [amountU256.low.toString(), amountU256.high.toString()], // u256 as [low, high]
        };
        console.log('🔍 test_jediswap_only call:', {
          contractAddress: call.contractAddress,
          entrypoint: call.entrypoint,
          calldata: call.calldata,
          amount: amount.toString(),
          amountU256: { low: amountU256.low.toString(), high: amountU256.high.toString() }
        });
        calls.push(call);
      } else if (item.testFunction === 'test_ekubo_only') {
        // Test with 0.1 STRK (100000000000000000 wei)
        const amount = BigInt('100000000000000000');
        const amountU256 = uint256.bnToUint256(amount);
        const call: Call = {
          contractAddress: contractAddress,
          entrypoint: 'test_ekubo_only',
          calldata: [amountU256.low.toString(), amountU256.high.toString()], // u256 as [low, high]
        };
        console.log('🔍 test_ekubo_only call:', {
          contractAddress: call.contractAddress,
          entrypoint: call.entrypoint,
          calldata: call.calldata,
          amount: amount.toString(),
          amountU256: { low: amountU256.low.toString(), high: amountU256.high.toString() }
        });
        calls.push(call);
      } else if (item.testFunction === 'accrue_yields' || item.testFunction === 'accrue_jediswap_yields' || item.testFunction === 'accrue_ekubo_yields') {
        const call: Call = {
          contractAddress: contractAddress,
          entrypoint: item.testFunction,
          calldata: [], // No parameters
        };
        calls.push(call);
      } else if (item.testFunction === 'rebalance') {
        const call: Call = {
          contractAddress: contractAddress,
          entrypoint: 'rebalance',
          calldata: [], // No parameters
        };
        calls.push(call);
      } else if (item.testFunction === 'get_position_counts') {
        // This is a query function - handle it separately
        // We'll call both getters and display the results
        try {
          const jediCount = await provider.callContract({
            contractAddress: contractAddress,
            entrypoint: 'get_jediswap_position_count',
            calldata: []
          });
          const ekuboCount = await provider.callContract({
            contractAddress: contractAddress,
            entrypoint: 'get_ekubo_position_count',
            calldata: []
          });
          
          // Parse results (u256 returns as [low, high])
          const jediLow = BigInt(jediCount[0] || '0');
          const jediHigh = BigInt(jediCount[1] || '0');
          const jediTotal = jediLow + (jediHigh << 128n);
          
          const ekuboLow = BigInt(ekuboCount[0] || '0');
          const ekuboHigh = BigInt(ekuboCount[1] || '0');
          const ekuboTotal = ekuboLow + (ekuboHigh << 128n);
          
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'success',
              message: `✅ Position Counts:\nJediSwap: ${jediTotal.toString()}\nEkubo: ${ekuboTotal.toString()}`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        } catch (error: any) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: `❌ Failed to query position counts: ${error.message}`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
      } else if (item.testFunction === 'get_user_balance') {
        // Query function - get balance for current user
        try {
          if (!address) {
            throw new Error('Wallet not connected');
          }
          const balanceResult = await provider.callContract({
            contractAddress: contractAddress,
            entrypoint: 'get_user_balance',
            calldata: [address] // user address
          });
          
          // Parse u256 result [low, high]
          const low = BigInt(balanceResult[0] || '0');
          const high = BigInt(balanceResult[1] || '0');
          const balance = low + (high << 128n);
          const balanceStrk = Number(balance) / 1e18;
          
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'success',
              message: `✅ Your Balance: ${balanceStrk.toFixed(6)} STRK (${balance.toString()} wei)`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        } catch (error: any) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: `❌ Failed to query balance: ${error.message}`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
      } else if (item.testFunction === 'get_allocation') {
        // Query function - get allocation percentages
        try {
          const allocationResult = await provider.callContract({
            contractAddress: contractAddress,
            entrypoint: 'get_allocation',
            calldata: []
          });
          
          // Parse results (felt252, felt252) - basis points
          const jediBps = Number(allocationResult[0] || '0');
          const ekuboBps = Number(allocationResult[1] || '0');
          const jediPct = jediBps / 100;
          const ekuboPct = ekuboBps / 100;
          
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'success',
              message: `✅ Allocation:\nJediSwap: ${jediPct}% (${jediBps} bps)\nEkubo: ${ekuboPct}% (${ekuboBps} bps)`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        } catch (error: any) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: `❌ Failed to query allocation: ${error.message}`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
      } else if (item.testFunction === 'commit_mist_deposit') {
        // MIST: Commit deposit (Phase 1) - requires hash and expected amount
        // For testing, generate a random secret and hash it
        // Note: In production, users compute hash(secret) on their side
        const secret = BigInt(Math.floor(Math.random() * Number.MAX_SAFE_INTEGER)).toString();
        const { hash } = await import('starknet');
        // Contract uses poseidon_hash_span([secret, secret]) to match frontend
        // computeHashOnElements uses Poseidon hash
        const commitmentHash = hash.computeHashOnElements([secret, secret]);
        const expectedAmount = BigInt('100000000000000000'); // 0.1 STRK for testing
        const amountU256 = uint256.bnToUint256(expectedAmount);
        
        const call: Call = {
          contractAddress: contractAddress,
          entrypoint: 'commit_mist_deposit',
          calldata: [
            commitmentHash,
            amountU256.low.toString(),
            amountU256.high.toString(),
          ],
        };
        
        // Store secret in localStorage for later reveal (testing only)
        localStorage.setItem(`mist_secret_${commitmentHash}`, secret);
        
        calls.push(call);
        console.log('🔍 MIST commit_mist_deposit call:', {
          commitmentHash,
          expectedAmount: expectedAmount.toString(),
          secret: '***stored in localStorage***',
        });
      } else if (item.testFunction === 'reveal_and_claim_mist_deposit') {
        // MIST: Reveal secret and claim (Phase 2)
        // For testing, prompt user for commitment hash or use stored secret
        const commitmentHash = prompt('Enter commitment hash (or leave empty to use last stored secret):');
        if (!commitmentHash) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: '❌ Commitment hash required',
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
        
        // Try to get secret from localStorage
        const secret = localStorage.getItem(`mist_secret_${commitmentHash}`);
        if (!secret) {
          const manualSecret = prompt('Secret not found in storage. Enter secret manually:');
          if (!manualSecret) {
            setTestResults(prev => ({
              ...prev,
              [item.id]: {
                status: 'error',
                message: '❌ Secret required',
                timestamp: new Date().toISOString()
              }
            }));
            setTesting(null);
            return;
          }
          
          const call: Call = {
            contractAddress: contractAddress,
            entrypoint: 'reveal_and_claim_mist_deposit',
            calldata: [manualSecret],
          };
          calls.push(call);
        } else {
          const call: Call = {
            contractAddress: contractAddress,
            entrypoint: 'reveal_and_claim_mist_deposit',
            calldata: [secret],
          };
          calls.push(call);
          // Remove secret from storage after use
          localStorage.removeItem(`mist_secret_${commitmentHash}`);
        }
        
        console.log('🔍 MIST reveal_and_claim_mist_deposit call:', {
          commitmentHash,
          secret: '***provided***',
        });
      } else if (item.testFunction === 'get_mist_commitment') {
        // MIST: Query commitment status (view function)
        const commitmentHash = prompt('Enter commitment hash to check:');
        if (!commitmentHash) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: '❌ Commitment hash required',
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
        
        try {
          const result = await provider.callContract({
            contractAddress: contractAddress,
            entrypoint: 'get_mist_commitment',
            calldata: [commitmentHash],
          });
          
          const user = result[0] || '0x0';
          const amountLow = BigInt(result[1] || '0');
          const amountHigh = BigInt(result[2] || '0');
          const amount = amountLow + (amountHigh << 128n);
          const revealed = result[3] === '1' || result[3] === 'true';
          
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'success',
              message: `✅ Commitment Status:\nHash: ${commitmentHash}\nUser: ${user}\nAmount: ${(Number(amount) / 1e18).toFixed(6)} STRK\nRevealed: ${revealed ? 'Yes' : 'No'}`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        } catch (error: any) {
          setTestResults(prev => ({
            ...prev,
            [item.id]: {
              status: 'error',
              message: `❌ Failed to query commitment: ${error.message}`,
              timestamp: new Date().toISOString()
            }
          }));
          setTesting(null);
          return;
        }
      } else if (item.testFunction === 'deposit' || item.testFunction === 'withdraw') {
        // These are handled by the main dashboard, but we can add test buttons here
        // For now, show a message directing users to the main dashboard
        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            status: 'info',
            message: `ℹ️ ${item.testFunction === 'deposit' ? 'Deposit' : 'Withdraw'} functionality is available in the main Dashboard. Use the deposit/withdraw buttons there.`,
            timestamp: new Date().toISOString()
          }
        }));
        setTesting(null);
        return;
      }

      if (calls.length === 0) {
        throw new Error('No test function available');
      }

      // Validate calls before execution
      for (let i = 0; i < calls.length; i++) {
        const call = calls[i];
        if (!call.contractAddress || typeof call.contractAddress !== 'string') {
          throw new Error(`Invalid contractAddress in call[${i}]`);
        }
        if (!call.entrypoint || typeof call.entrypoint !== 'string') {
          throw new Error(`Invalid entrypoint in call[${i}]`);
        }
        if (!Array.isArray(call.calldata)) {
          throw new Error(`Calldata must be array in call[${i}]`);
        }
        // Ensure all calldata values are strings (no undefined/null)
        for (let j = 0; j < call.calldata.length; j++) {
          const val = call.calldata[j];
          if (val === undefined || val === null) {
            throw new Error(`Calldata[${j}] is undefined/null in call[${i}]`);
          }
          // Convert to string if not already
          call.calldata[j] = String(val);
        }
      }

      // Log the full call structure for debugging
      console.log('📤 Executing calls:', JSON.stringify(calls, null, 2));

      // Execute transaction using account.execute()
      // Try single Call first, then fallback to array format
      let result;
      try {
        if (calls.length === 1) {
          result = await account!.execute(calls[0], undefined, { maxFee: undefined });
        } else {
          result = await account!.execute(calls, undefined, { maxFee: undefined });
        }
      } catch (executeError: any) {
        // If single format failed, try array format
        if (calls.length === 1 && executeError.message?.includes('array')) {
          console.log('Retrying with array format...');
          result = await account!.execute([calls[0]], undefined, { maxFee: undefined });
        } else {
          throw executeError;
        }
      }
      
      // Validate result structure
      if (!result || typeof result !== 'object') {
        throw new Error(`Invalid result from account.execute(): ${typeof result}`);
      }
      
      // Extract transaction hash - handle both string and object formats
      let txHash: string;
      if (typeof result.transaction_hash === 'string') {
        txHash = result.transaction_hash;
      } else if (result.transaction_hash && typeof result.transaction_hash === 'object') {
        // If it's an object, try to extract the hash
        txHash = String(result.transaction_hash);
        console.warn('⚠️ transaction_hash is an object, converted to string:', result.transaction_hash);
      } else {
        throw new Error(`Cannot extract transaction_hash from result: ${JSON.stringify(result)}`);
      }
      
      setTestResults(prev => ({
        ...prev,
        [item.id]: {
          status: 'pending',
          message: 'Transaction submitted, waiting for confirmation...',
          txHash: txHash,
          timestamp: new Date().toISOString()
        }
      }));

      // Wait for transaction to be confirmed and fetch receipt for gas fees
      // Reuse the provider we created earlier
      try {
        const receipt = await provider.waitForTransaction(txHash, { retryInterval: 2000 });
        
        // Extract gas fees from receipt with defensive parsing
        let gasFee = '0';
        let gasFeeWei = BigInt(0);
        try {
          const actualFee = (receipt as any).actual_fee;
          if (receipt && actualFee !== undefined && actualFee !== null) {
            // Handle both string and U256 object formats
            if (typeof actualFee === 'string') {
              if (actualFee.trim() !== '') {
                gasFeeWei = BigInt(actualFee);
              }
            } else if (actualFee && typeof actualFee === 'object') {
              // Handle new format: { amount: string; unit: "WEI" | "FRI" }
              if (actualFee.amount !== undefined) {
                gasFeeWei = BigInt(actualFee.amount);
              } else if (actualFee.low !== undefined && actualFee.high !== undefined) {
                // Handle old U256 format: {low: string, high: string}
                const lowStr = String(actualFee.low || '0');
                const highStr = String(actualFee.high || '0');
                if (lowStr !== '' && highStr !== '') {
                  const low = BigInt(lowStr);
                  const high = BigInt(highStr);
                  gasFeeWei = low + (high * BigInt(2 ** 128));
                }
              } else {
                // Object doesn't have expected structure - skip parsing
                // Log for debugging but don't try to convert
                console.warn('actual_fee is an object but not in expected format:', actualFee);
              }
            } else if (typeof actualFee === 'number') {
              gasFeeWei = BigInt(Math.floor(actualFee));
            }
            
            // Convert to STRK (assuming 18 decimals)
            if (gasFeeWei > 0n) {
              const gasFeeStrk = Number(gasFeeWei) / 1e18;
              gasFee = gasFeeStrk.toFixed(6);
            }
          }
        } catch (feeError: any) {
          console.warn('Error parsing gas fee from receipt:', feeError);
          // Continue without gas fee - transaction still succeeded
        }
        
        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            ...prev[item.id],
            status: 'success',
            message: gasFee !== '0' 
              ? `Transaction confirmed! Gas: ${gasFee} STRK`
              : 'Transaction confirmed!',
            gasFee: gasFee,
            gasFeeWei: gasFeeWei.toString(),
            receipt: receipt,
          }
        }));
        
        // Refresh yield and protocol stats after successful yield accrual
        if (item.testFunction === 'accrue_yields' || item.testFunction === 'accrue_jediswap_yields' || item.testFunction === 'accrue_ekubo_yields') {
          setTimeout(() => {
            fetchYield();
            fetchProtocolStats();
          }, 3000); // Wait 3 seconds for transaction to be indexed
        }
      } catch (waitError: any) {
        // Transaction was submitted but receipt waiting/parsing failed
        // Still show the transaction hash so user can verify on-chain
        console.error('Error waiting for transaction receipt:', waitError);
        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            ...prev[item.id],
            status: 'pending',
            message: `Transaction submitted (hash: ${txHash.slice(0, 10)}...). Receipt parsing failed: ${waitError.message || 'Unknown error'}. Check transaction on Starkscan.`,
            txHash: txHash,
          }
        }));
      }
      
      setTesting(null);
    } catch (error: any) {
      // Check if we already have a transaction hash (transaction was submitted)
      const existingResult = testResults[item.id];
      const existingTxHash = existingResult?.txHash;
      
      let errorMessage = error.message || 'Test failed';
      
      // If transaction was already submitted, preserve the hash and provide better error message
      if (existingTxHash) {
        errorMessage = `Transaction submitted (hash: ${existingTxHash.slice(0, 10)}...) but settlement failed: ${errorMessage}\n\n` +
          `The transaction was successfully submitted to the network. You can verify it on Starkscan.\n` +
          `The error occurred during receipt parsing or confirmation.`;
        
        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            ...prev[item.id],
            status: 'pending',
            message: errorMessage,
            txHash: existingTxHash,
            timestamp: prev[item.id]?.timestamp || new Date().toISOString(),
            fullError: error.toString(),
          }
        }));
        setTesting(null);
        return;
      }
      
      // Provide more helpful error messages
      if (errorMessage.includes('No pending deposits') || errorMessage.includes('0x4e6f2070656e64696e67206465706f73697473')) {
        errorMessage = `ℹ️ No Pending Deposits\n\n` +
          `The \`deploy_to_protocols\` function requires deposits to have been made first.\n\n` +
          `📋 Workflow:\n` +
          `1. First, use the "Deposit" function in the main dashboard to deposit STRK/ETH\n` +
          `2. Then call \`deploy_to_protocols\` to deploy those deposits to JediSwap V2 and Ekubo\n\n` +
          `💡 This is expected behavior - you need to deposit funds before they can be deployed to protocols.`;
      } else if (errorMessage.includes('ENTRYPOINT_NOT_FOUND')) {
        errorMessage = `Function not found. The contract may not have this entrypoint, or the contract address is incorrect. Contract: ${contractAddress}`;
      } else if (errorMessage.includes('not deployed') || errorMessage.includes('Contract not found')) {
        errorMessage = `Contract not found at ${contractAddress}. Please verify the contract was deployed and the RPC has indexed it.`;
      } else if (errorMessage.includes('Transaction was refused')) {
        errorMessage = 'Transaction was refused by your wallet. Please check your wallet and try again.';
      } else if (errorMessage.includes('Unauthorized') || errorMessage.includes('Only owner') || errorMessage.includes('owner can')) {
        const contractOwner = '0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d';
        errorMessage = `❌ Unauthorized: Owner-only function.\n\n` +
          `Your wallet: ${address}\n` +
          `Contract owner: ${contractOwner}\n\n` +
          `These test functions require the contract owner's wallet:\n` +
          `- deploy_to_protocols (owner or risk_engine)\n` +
          `- test_jediswap_only (owner only)\n` +
          `- test_ekubo_only (owner only)\n\n` +
          `💡 Solution: Toggle "Owner Wallet" mode above to execute via backend using owner's private key.\n\n` +
          `Note: deposit() and withdraw() are public - anyone can use them!`;
      } else if (errorMessage.includes('RPC: starknet_estimateFee') && errorMessage.includes('No pending deposits')) {
        // Handle RPC fee estimation errors that contain the actual contract error
        errorMessage = `ℹ️ No Pending Deposits (during fee estimation)\n\n` +
          `The contract rejected the transaction during fee estimation because there are no pending deposits.\n\n` +
          `📋 Workflow:\n` +
          `1. First, use the "Deposit" function in the main dashboard to deposit STRK/ETH\n` +
          `2. Then call \`deploy_to_protocols\` to deploy those deposits to JediSwap V2 and Ekubo\n\n` +
          `💡 This is expected behavior - you need to deposit funds before they can be deployed to protocols.`;
      }
      
      setTestResults(prev => ({
        ...prev,
        [item.id]: {
          status: 'error',
          message: errorMessage,
          timestamp: new Date().toISOString(),
          fullError: error.toString(),
          // Explicitly clear txHash - errors before transaction submission shouldn't show a hash
          // This prevents showing transaction hashes from previous tests
          txHash: undefined
        }
      }));
      setTesting(null);
    }
  }

  const categories = Array.from(new Set(checklist.map(item => item.category)));

  return (
    <div className="space-y-6 bg-white p-6 rounded-xl">
      <div>
        <h2 className="text-3xl font-bold text-slate-900 mb-2">Protocol Integration Status</h2>
        <p className="text-slate-600 text-base">
          Real-time testing and status of our dual-protocol liquidity deployment system.
        </p>
      </div>

      {/* Wallet Mode Selector */}
      <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-blue-900 mb-1">Wallet Mode</h3>
            <p className="text-sm text-blue-700">
              {useOwnerWallet 
                ? 'Using owner wallet (backend) for owner-only functions'
                : 'Using your connected wallet'}
            </p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={useOwnerWallet}
              onChange={(e) => setUseOwnerWallet(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            <span className="ml-3 text-sm font-medium text-blue-900">
              {useOwnerWallet ? 'Owner Wallet' : 'Your Wallet'}
            </span>
          </label>
        </div>
        {useOwnerWallet && (
          <div className="space-y-2 mt-3">
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
              <strong>⚠️ Development/Staging Only:</strong> Owner wallet API is <strong>disabled on production</strong> for security. On production, only the contract owner can execute owner-only functions directly via their wallet.
            </div>
            <div className="p-3 bg-blue-100 rounded-lg text-xs text-blue-800">
              Owner wallet mode requires <code className="bg-blue-200 px-1 rounded">OWNER_PRIVATE_KEY</code> or keystore file to be configured in backend environment variables.
            </div>
          </div>
        )}
        {!useOwnerWallet && (
          <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg text-xs text-green-800">
            <strong>✅ Production Ready:</strong> On production, owner-only functions can only be executed by the contract owner using their wallet. This is the secure, intended behavior.
          </div>
        )}
      </div>


      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-green-50 border-2 border-green-200 rounded-xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-green-700">
            {checklist.filter(i => i.status === 'completed').length}
          </div>
          <div className="text-sm font-medium text-green-800 mt-1">Completed</div>
        </div>
        <div className="bg-amber-50 border-2 border-amber-200 rounded-xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-amber-700">
            {checklist.filter(i => i.status === 'in_progress').length}
          </div>
          <div className="text-sm font-medium text-amber-800 mt-1">In Progress</div>
        </div>
        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-red-700">
            {checklist.filter(i => i.status === 'blocked').length}
          </div>
          <div className="text-sm font-medium text-red-800 mt-1">Blocked</div>
        </div>
        <div className="bg-slate-50 border-2 border-slate-200 rounded-xl p-5 shadow-sm">
          <div className="text-3xl font-bold text-slate-700">
            {checklist.filter(i => i.status === 'planned').length}
          </div>
          <div className="text-sm font-medium text-slate-800 mt-1">Planned</div>
        </div>
      </div>

      {/* Checklist by Category */}
      {categories.map(category => {
        const categoryItems = checklist.filter(item => item.category === category);
        return (
          <div key={category} className="border-2 border-slate-200 rounded-xl p-5 bg-slate-50 shadow-sm">
            <h3 className="text-xl font-bold text-slate-900 mb-4">{category}</h3>
            <div className="space-y-3">
              {categoryItems.map(item => (
                <div
                  key={item.id}
                  className={`border-2 rounded-xl p-4 ${getStatusColor(item.status)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-xl">{getStatusIcon(item.status)}</span>
                        <span className="font-semibold text-base">{item.name}</span>
                        <span className="text-xs px-2.5 py-1 rounded-md font-medium bg-white/70 border border-current/20">
                          {item.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm font-medium mb-2 opacity-90">{item.description}</p>
                      {item.notes && (
                        <p className="text-xs font-medium opacity-75 italic mb-2">{item.notes}</p>
                      )}
                      {item.testFunction && (
                        <div className="mt-2 text-xs font-mono opacity-70">
                          Function: <code className="bg-white/60 px-2 py-0.5 rounded border border-current/20">{item.testFunction}()</code>
                        </div>
                      )}
                      {testResults[item.id] && (
                        <div className="mt-3 p-2 rounded-lg bg-white/60 border border-current/20">
                          <div className={`text-xs font-semibold ${
                            testResults[item.id].status === 'success' ? 'text-green-800' :
                            testResults[item.id].status === 'error' ? 'text-red-800' :
                            testResults[item.id].status === 'pending' ? 'text-amber-800' :
                            'text-slate-800'
                          }`}>
                            {testResults[item.id].status === 'success' ? '✅' :
                             testResults[item.id].status === 'error' ? '❌' :
                             testResults[item.id].status === 'pending' ? '⏳' :
                             '🔄'} {testResults[item.id].message}
                          </div>
                          {testResults[item.id].txHash && (
                            <div className="text-xs font-mono opacity-70 mt-1 break-all">
                              TX: <a 
                                href={`https://sepolia.starkscan.co/tx/${testResults[item.id].txHash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:underline"
                              >
                                {testResults[item.id].txHash.slice(0, 20)}...
                              </a>
                            </div>
                          )}
                          {testResults[item.id].gasFee && (
                            <div className="text-xs opacity-70 mt-1">
                              Gas Fee: <span className="font-semibold">{testResults[item.id].gasFee} STRK</span>
                            </div>
                          )}
                          {testResults[item.id].timestamp && (
                            <div className="text-xs opacity-60 mt-1">
                              {new Date(testResults[item.id].timestamp).toLocaleString()}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    {item.testFunction && item.status !== 'planned' && (
                      <div className="flex gap-2 ml-4">
                        <button
                          onClick={handleDeposit}
                          disabled={depositing || !account || !address}
                          className="px-3 py-2 text-xs font-semibold bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                        >
                          {depositing ? 'Depositing...' : '📥 Deposit'}
                        </button>
                        <button
                          onClick={() => handleTest(item)}
                          disabled={testing === item.id || !account}
                          className="px-4 py-2 text-sm font-semibold bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                        >
                          {testing === item.id ? 'Testing...' : 'Test'}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {/* Contract Info */}
      <div className="border-2 border-slate-200 rounded-xl p-5 bg-slate-50 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 mb-3">Contract Information</h3>
        <div className="text-sm space-y-2 font-medium">
          <div>
            <span className="text-slate-700">Contract Address:</span>{' '}
            <code className="bg-white px-2 py-1 rounded text-xs font-mono border border-slate-300">
              {contractAddress || 'Loading...'}
            </code>
          </div>
          <div>
            <span className="text-slate-700">Network:</span>{' '}
            <span className="text-slate-900">Starknet Sepolia Testnet</span>
          </div>
          <div>
            <span className="text-slate-700">Status:</span>{' '}
            <span className="text-slate-900">{router.isLoading ? 'Loading...' : 'Connected'}</span>
          </div>
          <div>
            <span className="text-slate-700">Total Yield Accrued:</span>{' '}
            <span className="text-slate-900 font-semibold">
              {yieldLoading ? 'Loading...' : `${totalYield} STRK`}
            </span>
            <button
              onClick={() => { fetchYield(); fetchProtocolStats(); }}
              className="ml-2 px-2 py-1 text-xs bg-slate-200 hover:bg-slate-300 rounded transition-colors"
              title="Refresh stats"
            >
              🔄
            </button>
          </div>
        </div>
      </div>

      {/* Proof status (L2/L1) */}
      <div className="border-2 border-emerald-200 rounded-xl p-5 bg-emerald-50 shadow-sm mt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-emerald-900">Proof Verification (L2/L1)</h3>
          <button
            onClick={proofHistory.refetch}
            className="px-3 py-1 text-sm bg-emerald-600 text-white rounded hover:bg-emerald-700 transition-colors"
          >
            Refresh
          </button>
        </div>
        {proofHistory.loading && <p className="text-sm text-emerald-700">Loading proof history…</p>}
        {proofHistory.error && <p className="text-sm text-red-600">Error: {proofHistory.error}</p>}
        {proofHistory.data.length === 0 && !proofHistory.loading && (
          <p className="text-sm text-emerald-700">No proofs yet.</p>
        )}
        {proofHistory.data.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm text-left border-collapse">
              <thead>
                <tr className="text-xs uppercase text-emerald-800">
                  <th className="py-2 pr-4">Time</th>
                  <th className="py-2 pr-4">Proof</th>
                  <th className="py-2 pr-4">Tx</th>
                  <th className="py-2 pr-4">L2 Fact</th>
                  <th className="py-2 pr-4">L1 Fact</th>
                  <th className="py-2 pr-4">Atlantic</th>
                  <th className="py-2 pr-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {proofHistory.data.slice(0, 8).map((p) => (
                  <tr key={p.id} className="border-t border-emerald-100 align-top">
                    <td className="py-2 pr-4 text-slate-700">
                      {p.timestamp ? new Date(p.timestamp).toLocaleString() : '—'}
                    </td>
                    <td className="py-2 pr-4 text-slate-700">
                      {(p.proof_hash || '').slice(0, 12)}…
                    </td>
                    <td className="py-2 pr-4 text-slate-700">
                      {p.tx_hash ? `${p.tx_hash.slice(0, 10)}…` : '—'}
                    </td>
                    <td className="py-2 pr-4 text-slate-700">
                      {(p.l2_fact_hash || p.fact_hash || '—').slice(0, 12)}…
                      {p.l2_verified_at ? (
                        <div className="text-[11px] text-emerald-700">
                          ✓ {new Date(p.l2_verified_at).toLocaleString()}
                        </div>
                      ) : (
                        <div className="text-[11px] text-amber-700">pending</div>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-slate-700">
                      {(p.l1_fact_hash || '—').slice(0, 12)}…
                      {p.l1_verified_at ? (
                        <div className="text-[11px] text-emerald-700">
                          ✓ {new Date(p.l1_verified_at).toLocaleString()}
                        </div>
                      ) : p.l1_fact_hash ? (
                        <div className="text-[11px] text-amber-700">pending</div>
                      ) : null}
                    </td>
                    <td className="py-2 pr-4 text-slate-700">
                      {p.atlantic_query_id ? p.atlantic_query_id.slice(0, 10) + '…' : '—'}
                    </td>
                    <td className="py-2 pr-4">
                      <ProofBadge
                        hash={p.proof_hash}
                        status={p.proof_status as any}
                        txHash={p.tx_hash}
                        factHash={p.fact_hash}
                        l2FactHash={p.l2_fact_hash}
                        l2VerifiedAt={p.l2_verified_at}
                        l1FactHash={p.l1_fact_hash}
                        l1VerifiedAt={p.l1_verified_at}
                        network={p.network}
                        submittedAt={p.timestamp || undefined}
                        verifiedAt={p.l2_verified_at || p.l1_verified_at || undefined}
                        atlanticQueryId={p.atlantic_query_id}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Protocol Statistics */}
      <div className="border-2 border-purple-200 rounded-xl p-5 bg-purple-50 shadow-sm mt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-purple-900">Protocol Statistics</h3>
          <button
            onClick={fetchProtocolStats}
            disabled={statsLoading}
            className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            {statsLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* JediSwap Stats */}
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-md font-semibold text-purple-800">JediSwap</h4>
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">DEX</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">TVL:</span>
                <span className="font-semibold text-slate-900">
                  {statsLoading ? 'Loading...' : `${protocolStats.jediswap.tvl} STRK`}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Estimated APY:</span>
                <span className="font-semibold text-green-600">
                  {statsLoading ? 'Loading...' : `${protocolStats.jediswap.apy}%`}
                </span>
              </div>
            </div>
          </div>

          {/* Ekubo Stats */}
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-md font-semibold text-purple-800">Ekubo</h4>
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">DEX</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-600">TVL:</span>
                <span className="font-semibold text-slate-900">
                  {statsLoading ? 'Loading...' : `${protocolStats.ekubo.tvl} STRK`}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Estimated APY:</span>
                <span className="font-semibold text-green-600">
                  {statsLoading ? 'Loading...' : `${protocolStats.ekubo.apy}%`}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="mt-3 text-xs text-slate-500 italic">
          Note: APY is estimated based on total yield accrued. Actual APY may vary based on market conditions and time period.
        </div>
      </div>

      {/* Development Log Section */}
      <div className="border-2 border-blue-200 rounded-xl p-5 bg-blue-50 shadow-sm mt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-blue-900">Development Log</h3>
          <button
            onClick={() => {
              setDevLogLoading(true);
              fetch('/api/integration-tests/dev-log')
                .then(res => res.json())
                .then(data => {
                  if (data.success) {
                    setDevLog(data.content);
                  }
                  setDevLogLoading(false);
                })
                .catch(error => {
                  console.error('Error refreshing dev log:', error);
                  setDevLogLoading(false);
                });
            }}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            {devLogLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
        <div className="bg-white rounded-lg p-4 border border-blue-200 max-h-96 overflow-y-auto">
          {devLogLoading ? (
            <div className="text-slate-500 text-center py-4">Loading dev log...</div>
          ) : (
            <pre className="text-xs font-mono whitespace-pre-wrap text-slate-700">
              {devLog || 'No log content available'}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
