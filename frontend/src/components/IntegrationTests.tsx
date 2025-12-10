'use client';

import { useState } from 'react';
import { useAccount, useContractWrite, useWaitForTransactionReceipt } from '@starknet-react/core';
import { useStrategyRouterV2 } from '@/hooks/useStrategyRouterV2';
import { getConfig } from '@/lib/config';
import { Call } from 'starknet';

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
  const { writeAsync, data: txHash } = useContractWrite();
  const { isLoading: isTxLoading, isSuccess: isTxSuccess, error: txError } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const config = getConfig();
  const contractAddress = config.strategyRouterAddress;

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
      const calls: Call[] = [];
      
      if (item.testFunction === 'deploy_to_protocols') {
        calls.push({
          contractAddress,
          entrypoint: 'deploy_to_protocols',
          calldata: [],
        });
      } else if (item.testFunction === 'test_jediswap_only') {
        // Test with 0.1 STRK (100000000000000000 wei)
        const amount = '100000000000000000';
        calls.push({
          contractAddress,
          entrypoint: 'test_jediswap_only',
          calldata: [amount, '0'], // u256: low, high
        });
      } else if (item.testFunction === 'test_ekubo_only') {
        // Test with 0.1 STRK (100000000000000000 wei)
        const amount = '100000000000000000';
        calls.push({
          contractAddress,
          entrypoint: 'test_ekubo_only',
          calldata: [amount, '0'], // u256: low, high
        });
      }

      if (calls.length === 0) {
        throw new Error('No test function available');
      }

      const result = await writeAsync({ calls });
      
      setTestResults(prev => ({
        ...prev,
        [item.id]: {
          status: 'pending',
          message: 'Transaction submitted, waiting for confirmation...',
          txHash: result.transaction_hash,
          timestamp: new Date().toISOString()
        }
      }));

      // Wait for transaction to be confirmed
      // The useWaitForTransactionReceipt hook will handle this
    } catch (error: any) {
      setTestResults(prev => ({
        ...prev,
        [item.id]: {
          status: 'error',
          message: error.message || 'Test failed',
          timestamp: new Date().toISOString()
        }
      }));
      setTesting(null);
    }
  };

  // Update test results when transaction status changes
  if (txHash && testing) {
    if (isTxSuccess) {
      setTestResults(prev => ({
        ...prev,
        [testing]: {
          ...prev[testing],
          status: 'success',
          message: 'Transaction confirmed successfully!',
        }
      }));
      setTesting(null);
    } else if (txError) {
      setTestResults(prev => ({
        ...prev,
        [testing]: {
          ...prev[testing],
          status: 'error',
          message: txError.message || 'Transaction failed',
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
                              TX: {testResults[item.id].txHash.slice(0, 20)}...
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
                        disabled={testing === item.id || !account || isTxLoading}
                        className="ml-4 px-4 py-2 text-sm font-semibold bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                      >
                        {testing === item.id ? (isTxLoading ? 'Confirming...' : 'Testing...') : 'Test'}
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
    </div>
  );
}
