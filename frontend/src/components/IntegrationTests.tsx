'use client';

import { useState, useEffect } from 'react';
import { useAccount } from '@starknet-react/core';
import { useStrategyRouterV2 } from '@/hooks/useStrategyRouterV2';
import { getConfig } from '@/lib/config';
import { Call, RpcProvider, Contract } from 'starknet';

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

  const config = getConfig();
  const contractAddress = config.strategyRouterAddress;

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
      notes: '✅ Working - tested successfully'
    },
    {
      id: 'withdraw',
      category: 'Core',
      name: 'STRK Withdrawal',
      status: 'completed',
      description: 'Users can withdraw STRK from the Strategy Router',
      notes: '✅ Working - tested successfully'
    },
    {
      id: 'balance_tracking',
      category: 'Core',
      name: 'Balance Tracking',
      status: 'completed',
      description: 'Contract tracks user balances correctly',
      notes: '✅ Working'
    },

    // JediSwap Integration
    {
      id: 'jediswap_router_swap',
      category: 'JediSwap',
      name: 'JediSwap V2 Router - Swap',
      status: 'completed',
      description: 'Swap STRK to ETH using JediSwap V2 Router exact_input_single()',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Working - Fixed u32 fee type and 10000 tier'
    },
    {
      id: 'jediswap_nft_mint',
      category: 'JediSwap',
      name: 'JediSwap NFT Position Manager - Mint',
      status: 'completed',
      description: 'Add liquidity via NFT Position Manager mint() with I32 ticks',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Working - Fixed I32 struct and tick alignment (887200)'
    },
    {
      id: 'jediswap_full_integration',
      category: 'JediSwap',
      name: 'JediSwap Full Integration',
      status: 'completed',
      description: 'Complete flow: Swap + Add Liquidity + Track Position',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Fully working - All fixes applied'
    },

    // Ekubo Integration
    {
      id: 'ekubo_positions_mint',
      category: 'Ekubo',
      name: 'Ekubo Positions - Mint & Deposit',
      status: 'completed',
      description: 'Add liquidity via Ekubo Positions mint_and_deposit()',
      testFunction: 'test_ekubo_only',
      notes: '✅ Working - Using Positions contract (handles lock pattern)'
    },
    {
      id: 'ekubo_swap',
      category: 'Ekubo',
      name: 'Ekubo - Swap STRK to ETH',
      status: 'completed',
      description: 'Swap STRK to ETH before adding liquidity (uses JediSwap router)',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Working - Integrated into deploy_to_protocols flow'
    },
    {
      id: 'ekubo_full_integration',
      category: 'Ekubo',
      name: 'Ekubo Full Integration',
      status: 'completed',
      description: 'Complete flow: Swap + Add Liquidity + Track Position',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Fully working - All fixes applied'
    },

    // Protocol Deployment
    {
      id: 'deploy_both_protocols',
      category: 'Deployment',
      name: 'Deploy to Both Protocols',
      status: 'completed',
      description: 'deploy_to_protocols() - Deploy pending deposits to JediSwap and Ekubo',
      testFunction: 'deploy_to_protocols',
      notes: '✅ Fully working - Successfully tested on Sepolia'
    },
    {
      id: 'allocation_management',
      category: 'Deployment',
      name: 'Allocation Management',
      status: 'completed',
      description: 'Update allocation percentages between protocols',
      notes: '✅ Working'
    },

    // Advanced Features
    {
      id: 'position_tracking',
      category: 'Advanced',
      name: 'Position Tracking',
      status: 'in_progress',
      description: 'Store and track NFT position IDs from JediSwap and Ekubo',
      notes: 'Currently tracking counts, NFT IDs coming soon'
    },
    {
      id: 'yield_accrual',
      category: 'Advanced',
      name: 'Yield Accrual',
      status: 'in_progress',
      description: 'Accrue yields from liquidity positions',
      notes: 'Function exists but returns 0 - needs implementation'
    },
    {
      id: 'rebalancing',
      category: 'Advanced',
      name: 'Rebalancing',
      status: 'planned',
      description: 'Rebalance positions based on allocation changes',
      notes: 'Function exists but needs position management logic'
    },
    {
      id: 'slippage_protection',
      category: 'Advanced',
      name: 'Slippage Protection',
      status: 'planned',
      description: 'Add slippage protection for swaps and liquidity provision',
      notes: 'Currently set to 0 (no protection)'
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
    if (!item.testFunction || !account || !address || !contractAddress) {
      alert('Test function not available or wallet not connected');
      return;
    }

    setTesting(item.id);
    setTestResults(prev => ({ ...prev, [item.id]: { status: 'testing', message: 'Preparing transaction...' } }));

    try {
      // Verify contract is accessible before attempting transaction
      const provider = new RpcProvider({ nodeUrl: config.rpcUrl });
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

      // Create contract instance to properly format calls
      const routerContract = new Contract(STRATEGY_ROUTER_V2_ABI, contractAddress, provider);
      routerContract.connect(account);

      const calls: Call[] = [];
      
      if (item.testFunction === 'deploy_to_protocols') {
        const call = routerContract.populate('deploy_to_protocols', []);
        console.log('🔍 deploy_to_protocols call:', {
          contractAddress: call.contractAddress,
          entrypoint: call.entrypoint,
          calldata: call.calldata
        });
        calls.push(call);
      } else if (item.testFunction === 'test_jediswap_only') {
        // Test with 0.1 STRK (100000000000000000 wei)
        const amount = BigInt('100000000000000000');
        const call = routerContract.populate('test_jediswap_only', [amount]);
        console.log('🔍 test_jediswap_only call:', {
          contractAddress: call.contractAddress,
          entrypoint: call.entrypoint,
          calldata: call.calldata,
          amount: amount.toString()
        });
        calls.push(call);
      } else if (item.testFunction === 'test_ekubo_only') {
        // Test with 0.1 STRK (100000000000000000 wei)
        const amount = BigInt('100000000000000000');
        const call = routerContract.populate('test_ekubo_only', [amount]);
        console.log('🔍 test_ekubo_only call:', {
          contractAddress: call.contractAddress,
          entrypoint: call.entrypoint,
          calldata: call.calldata,
          amount: amount.toString()
        });
        calls.push(call);
      }

      if (calls.length === 0) {
        throw new Error('No test function available');
      }

      // Log the full call structure for debugging
      console.log('📤 Executing calls:', JSON.stringify(calls, null, 2));

      // Execute transaction using account.execute()
      const result = await account.execute(calls);
      
      setTestResults(prev => ({
        ...prev,
        [item.id]: {
          status: 'pending',
          message: 'Transaction submitted, waiting for confirmation...',
          txHash: result.transaction_hash,
          timestamp: new Date().toISOString()
        }
      }));

      // Wait for transaction to be confirmed and fetch receipt for gas fees
      // Reuse the provider we created earlier
      try {
        const receipt = await provider.waitForTransaction(result.transaction_hash, { retryInterval: 2000 });
        
        // Extract gas fees from receipt
        let gasFee = '0';
        let gasFeeWei = BigInt(0);
        if (receipt.actual_fee) {
          // Handle both string and U256 object formats
          if (typeof receipt.actual_fee === 'string') {
            gasFeeWei = BigInt(receipt.actual_fee);
          } else if (receipt.actual_fee.low !== undefined && receipt.actual_fee.high !== undefined) {
            // U256 format: {low: string, high: string}
            const low = BigInt(receipt.actual_fee.low);
            const high = BigInt(receipt.actual_fee.high);
            gasFeeWei = low + (high * BigInt(2 ** 128));
          } else {
            gasFeeWei = BigInt(String(receipt.actual_fee));
          }
          // Convert to STRK (assuming 18 decimals)
          const gasFeeStrk = Number(gasFeeWei) / 1e18;
          gasFee = gasFeeStrk.toFixed(6);
        }
        
        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            ...prev[item.id],
            status: 'success',
            message: `Transaction confirmed! Gas: ${gasFee} STRK`,
            gasFee: gasFee,
            gasFeeWei: gasFeeWei.toString(),
            receipt: receipt,
          }
        }));
      } catch (waitError: any) {
        setTestResults(prev => ({
          ...prev,
          [item.id]: {
            ...prev[item.id],
            status: 'error',
            message: waitError.message || 'Transaction confirmation failed',
          }
        }));
      }
      
      setTesting(null);
    } catch (error: any) {
      let errorMessage = error.message || 'Test failed';
      
      // Provide more helpful error messages
      if (errorMessage.includes('ENTRYPOINT_NOT_FOUND')) {
        errorMessage = `Function not found. The contract may not have this entrypoint, or the contract address is incorrect. Contract: ${contractAddress}`;
      } else if (errorMessage.includes('not deployed') || errorMessage.includes('Contract not found')) {
        errorMessage = `Contract not found at ${contractAddress}. Please verify the contract was deployed and the RPC has indexed it.`;
      } else if (errorMessage.includes('Transaction was refused')) {
        errorMessage = 'Transaction was refused by your wallet. Please check your wallet and try again.';
      } else if (errorMessage.includes('Only owner') || errorMessage.includes('owner can')) {
        errorMessage = `❌ Owner-only function. This test requires the contract owner's wallet. Your wallet (${address}) is not the contract owner. Only the owner can call: deploy_to_protocols, test_jediswap_only, test_ekubo_only`;
      }
      
      setTestResults(prev => ({
        ...prev,
        [item.id]: {
          status: 'error',
          message: errorMessage,
          timestamp: new Date().toISOString(),
          fullError: error.toString()
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
                      <button
                        onClick={() => handleTest(item)}
                        disabled={testing === item.id || !account}
                        className="ml-4 px-4 py-2 text-sm font-semibold bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                      >
                        {testing === item.id ? 'Testing...' : 'Test'}
                      </button>
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
