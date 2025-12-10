'use client';

import { useState, useEffect } from 'react';
import { useAccount } from '@starknet-react/core';
import { useStrategyRouterV2 } from '@/hooks/useStrategyRouterV2';
import { getConfig } from '@/lib/config';
import { Call, RpcProvider, Contract, uint256 } from 'starknet';

// Strategy Router V2 ABI including test functions
const STRATEGY_ROUTER_V2_ABI = [
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
  const routerV2 = useStrategyRouterV2();
  const [testing, setTesting] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [devLog, setDevLog] = useState<string>('');
  const [devLogLoading, setDevLogLoading] = useState(true);
  const [useOwnerWallet, setUseOwnerWallet] = useState(false);
  const [depositing, setDepositing] = useState(false);

  const config = getConfig();
  const contractAddress = config.strategyRouterAddress;
  const STRK_TOKEN_ADDRESS = '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d';
  
  // Functions that require owner access
  const ownerOnlyFunctions = ['deploy_to_protocols', 'test_jediswap_only', 'test_ekubo_only', 'accrue_yields', 'accrue_jediswap_yields', 'accrue_ekubo_yields'];

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
  }, []);

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
      id: 'slippage_protection',
      category: 'Advanced',
      name: 'Slippage Protection',
      status: 'planned',
      description: 'Add slippage protection for swaps and liquidity provision',
      notes: 'Currently set to 0 (no protection) - requires contract modification'
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
            if (receipt.actual_fee) {
              try {
                if (typeof receipt.actual_fee === 'string') {
                  gasFeeWei = BigInt(receipt.actual_fee);
                } else if (receipt.actual_fee && typeof receipt.actual_fee === 'object') {
                  const low = BigInt(receipt.actual_fee.low || '0');
                  const high = BigInt(receipt.actual_fee.high || '0');
                  gasFeeWei = low + (high << 128n);
                }
              } catch (e) {
                console.warn('Could not parse gas fee:', e);
              }
            }
            
            const gasFeeEth = Number(gasFeeWei) / 1e18;
            const isSuccess = receipt.status === 'ACCEPTED_ON_L2' || receipt.status === 'ACCEPTED_ON_L1';
            
            setTestResults(prev => ({
              ...prev,
              [item.id]: {
                status: isSuccess ? 'success' : 'error',
                message: isSuccess 
                  ? `✅ Success! Transaction confirmed on-chain. Gas: ${gasFeeEth.toFixed(6)} ETH`
                  : `Transaction ${receipt.status}`,
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
        if (receipt.actual_fee) {
          try {
            if (typeof receipt.actual_fee === 'string') {
              gasFeeWei = BigInt(receipt.actual_fee);
            } else if (receipt.actual_fee && typeof receipt.actual_fee === 'object') {
              const low = BigInt(receipt.actual_fee.low || '0');
              const high = BigInt(receipt.actual_fee.high || '0');
              gasFeeWei = low + (high << 128n);
            }
          } catch (e) {
            console.warn('Could not parse gas fee:', e);
          }
        }

        const gasFeeEth = Number(gasFeeWei) / 1e18;
        const gasFeeLink = `https://sepolia.voyager.online/tx/${data.transactionHash}`;

        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            status: receipt.status === 'ACCEPTED_ON_L2' || receipt.status === 'ACCEPTED_ON_L1' ? 'success' : 'error',
            message: receipt.status === 'ACCEPTED_ON_L2' || receipt.status === 'ACCEPTED_ON_L1' 
              ? `✅ Success! Executed via owner wallet. Gas: ${gasFeeEth.toFixed(6)} ETH`
              : `Transaction ${receipt.status}`,
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
          if (receipt && receipt.actual_fee !== undefined && receipt.actual_fee !== null) {
            // Handle both string and U256 object formats
            if (typeof receipt.actual_fee === 'string') {
              if (receipt.actual_fee.trim() !== '') {
                gasFeeWei = BigInt(receipt.actual_fee);
              }
            } else if (receipt.actual_fee && typeof receipt.actual_fee === 'object') {
              // U256 format: {low: string, high: string}
              if (receipt.actual_fee.low !== undefined && receipt.actual_fee.high !== undefined) {
                const lowStr = String(receipt.actual_fee.low || '0');
                const highStr = String(receipt.actual_fee.high || '0');
                if (lowStr !== '' && highStr !== '') {
                  const low = BigInt(lowStr);
                  const high = BigInt(highStr);
                  gasFeeWei = low + (high * BigInt(2 ** 128));
                }
              } else {
                // Object doesn't have low/high structure - skip parsing
                // Log for debugging but don't try to convert
                console.warn('actual_fee is an object but not in U256 format:', receipt.actual_fee);
              }
            } else if (typeof receipt.actual_fee === 'number') {
              gasFeeWei = BigInt(Math.floor(receipt.actual_fee));
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
            <span className="text-slate-900">{routerV2.isLoading ? 'Loading...' : 'Connected'}</span>
          </div>
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
