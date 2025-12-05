'use client';

import { useAccount } from '@starknet-react/core';
import { useRiskEngine } from '@/hooks/useRiskEngine';
import { useMistCash } from '@/hooks/useMistCash';
import { useState } from 'react';

const RISK_ENGINE_ADDRESS = process.env.NEXT_PUBLIC_RISK_ENGINE_ADDRESS || '';

export function Dashboard() {
  const { account, address } = useAccount();
  const { riskScore } = useRiskEngine(RISK_ENGINE_ADDRESS);
  const { mistService, isConnected } = useMistCash();
  const [depositAmount, setDepositAmount] = useState('');

  const handleDeposit = async () => {
    if (!mistService || !address || !depositAmount) return;
    
    try {
      const amount = BigInt(parseFloat(depositAmount) * 1e18);
      const claimingKey = 'your-claiming-key'; // Generate securely
      const txHash = await mistService.deposit(amount, address, claimingKey);
      console.log('Deposit tx:', txHash);
      alert(`Deposit successful! TX: ${txHash}`);
    } catch (error) {
      console.error('Deposit error:', error);
      alert('Deposit failed');
    }
  };

  if (!account) {
    return (
      <div className="text-center p-8">
        <p className="text-xl mb-4">Please connect your wallet to view the dashboard</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Pool Overview</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total TVL</p>
            <p className="text-2xl font-bold">0 ETH</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Current APY</p>
            <p className="text-2xl font-bold">0.00%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Risk Score</p>
            <p className="text-2xl font-bold">{riskScore?.toString() || 'N/A'}</p>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Current Allocation</h2>
        <div className="space-y-2">
          <div>
            <div className="flex justify-between mb-1">
              <span>Aave</span>
              <span>33.3%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '33.3%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span>Lido</span>
              <span>33.3%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-purple-600 h-2 rounded-full" style={{ width: '33.3%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span>Compound</span>
              <span>33.4%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: '33.4%' }}></div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Actions</h2>
        <div className="space-y-4">
          <div>
            <label className="block mb-2">Deposit Amount (ETH)</label>
            <input
              type="number"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="0.0"
            />
            <button
              onClick={handleDeposit}
              className="mt-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Deposit via MIST.cash
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Recent AI Decisions</h2>
        <p className="text-gray-600 dark:text-gray-400">No decisions yet</p>
      </div>
    </div>
  );
}

