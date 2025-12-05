'use client';

import { useAccount } from '@starknet-react/core';
import { useRiskEngine } from '@/hooks/useRiskEngine';
import { useMistCash } from '@/hooks/useMistCash';
import { useStrategyRouter } from '@/hooks/useStrategyRouter';
import { useDAOConstraints } from '@/hooks/useDAOConstraints';
import { useState } from 'react';

const RISK_ENGINE_ADDRESS = process.env.NEXT_PUBLIC_RISK_ENGINE_ADDRESS || '';
const STRATEGY_ROUTER_ADDRESS = process.env.NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS || '';
const DAO_CONSTRAINT_ADDRESS = process.env.NEXT_PUBLIC_DAO_CONSTRAINT_MANAGER_ADDRESS || '';

export function Dashboard() {
  const { account, address } = useAccount();
  const { riskScore } = useRiskEngine(RISK_ENGINE_ADDRESS);
  const { mistService, isConnected } = useMistCash();
  const { allocation, isLoading: allocationLoading, updateAllocation, isUpdating } = useStrategyRouter(STRATEGY_ROUTER_ADDRESS);
  const { constraints, isLoading: constraintsLoading } = useDAOConstraints(DAO_CONSTRAINT_ADDRESS);
  const [depositAmount, setDepositAmount] = useState('');
  const [allocationForm, setAllocationForm] = useState({ nostra: 33, zklend: 33, ekubo: 34 });

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

  const handleUpdateAllocation = async () => {
    if (!account) {
      alert('Please connect your wallet');
      return;
    }

    const total = allocationForm.nostra + allocationForm.zklend + allocationForm.ekubo;
    if (Math.abs(total - 100) > 0.1) {
      alert('Allocation must total 100%');
      return;
    }

    try {
      const nostra = Math.round(allocationForm.nostra * 100); // Convert to basis points
      const zklend = Math.round(allocationForm.zklend * 100);
      const ekubo = Math.round(allocationForm.ekubo * 100);
      
      const txHash = await updateAllocation(nostra, zklend, ekubo);
      alert(`Allocation updated! TX: ${txHash}`);
    } catch (error) {
      console.error('Update allocation error:', error);
      alert('Failed to update allocation');
    }
  };

  if (!account) {
    return (
      <div className="text-center p-8">
        <p className="text-xl mb-4 text-gray-300">Please connect your wallet to view the dashboard</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
          <div className="bg-black/30 backdrop-blur-md border border-purple-500/20 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">Pool Overview</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-purple-600/20 p-4 rounded-lg border border-purple-500/30">
            <p className="text-sm text-gray-400 mb-1">Total TVL</p>
            <p className="text-2xl font-bold text-white">0 STRK</p>
          </div>
          <div className="bg-blue-600/20 p-4 rounded-lg border border-blue-500/30">
            <p className="text-sm text-gray-400 mb-1">Current APY</p>
            <p className="text-2xl font-bold text-white">0.00%</p>
          </div>
          <div className="bg-green-600/20 p-4 rounded-lg border border-green-500/30">
            <p className="text-sm text-gray-400 mb-1">Risk Score</p>
            <p className="text-2xl font-bold text-white">{riskScore?.toString() || 'N/A'}</p>
          </div>
        </div>
      </div>

      <div className="bg-black/30 backdrop-blur-md border border-purple-500/20 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">Current Allocation</h2>
        {allocationLoading ? (
          <p className="text-gray-400">Loading allocation...</p>
        ) : allocation ? (
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-300 font-medium">Nostra (Lending)</span>
                <span className="text-blue-400 font-bold">{(Number(allocation.nostra_pct) / 100).toFixed(2)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full shadow-lg" style={{ width: `${Number(allocation.nostra_pct) / 100}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-300 font-medium">zkLend (Lending)</span>
                <span className="text-purple-400 font-bold">{(Number(allocation.zklend_pct) / 100).toFixed(2)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 h-3 rounded-full shadow-lg" style={{ width: `${Number(allocation.zklend_pct) / 100}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-300 font-medium">Ekubo (DEX/Liquidity)</span>
                <span className="text-green-400 font-bold">{(Number(allocation.ekubo_pct) / 100).toFixed(2)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div className="bg-gradient-to-r from-green-500 to-green-600 h-3 rounded-full shadow-lg" style={{ width: `${Number(allocation.ekubo_pct) / 100}%` }}></div>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-gray-400">No allocation data available</p>
        )}
      </div>

      {/* Update Allocation Section */}
      <div className="bg-black/30 backdrop-blur-md border border-purple-500/20 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">Update Allocation</h2>
        <div className="space-y-4">
          <div>
            <label className="block mb-2 text-gray-300 font-medium">Nostra (Lending) %</label>
            <input
              type="number"
              value={allocationForm.nostra}
              onChange={(e) => setAllocationForm({ ...allocationForm, nostra: parseFloat(e.target.value) || 0 })}
              className="w-full p-3 bg-black/50 border border-purple-500/30 rounded-lg text-white"
            />
          </div>
          <div>
            <label className="block mb-2 text-gray-300 font-medium">zkLend (Lending) %</label>
            <input
              type="number"
              value={allocationForm.zklend}
              onChange={(e) => setAllocationForm({ ...allocationForm, zklend: parseFloat(e.target.value) || 0 })}
              className="w-full p-3 bg-black/50 border border-purple-500/30 rounded-lg text-white"
            />
          </div>
          <div>
            <label className="block mb-2 text-gray-300 font-medium">Ekubo (DEX) %</label>
            <input
              type="number"
              value={allocationForm.ekubo}
              onChange={(e) => setAllocationForm({ ...allocationForm, ekubo: parseFloat(e.target.value) || 0 })}
              className="w-full p-3 bg-black/50 border border-purple-500/30 rounded-lg text-white"
            />
          </div>
          <button
            onClick={handleUpdateAllocation}
            disabled={isUpdating}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white rounded-lg font-semibold transition-all transform hover:scale-105 shadow-lg disabled:opacity-50"
          >
            {isUpdating ? '⏳ Updating...' : '🔄 Update Allocation'}
          </button>
        </div>
      </div>

      <div className="bg-black/30 backdrop-blur-md border border-purple-500/20 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">Actions</h2>
        <div className="space-y-4">
          <div>
            <label className="block mb-2 text-gray-300 font-medium">Deposit Amount (STRK)</label>
            <input
              type="number"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              className="w-full p-3 bg-black/50 border border-purple-500/30 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              placeholder="0.0"
            />
            <button
              onClick={handleDeposit}
              className="mt-3 w-full px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white rounded-lg font-semibold transition-all transform hover:scale-105 shadow-lg"
            >
              💰 Deposit via MIST.cash
            </button>
          </div>
        </div>
      </div>

      {/* DAO Constraints Section */}
      <div className="bg-black/30 backdrop-blur-md border border-purple-500/20 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">DAO Constraints</h2>
        {constraintsLoading ? (
          <p className="text-gray-400">Loading constraints...</p>
        ) : constraints ? (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-purple-600/20 p-4 rounded-lg border border-purple-500/30">
              <p className="text-sm text-gray-400 mb-1">Max Single Protocol</p>
              <p className="text-xl font-bold text-white">{(Number(constraints.max_single_protocol) / 100).toFixed(0)}%</p>
            </div>
            <div className="bg-blue-600/20 p-4 rounded-lg border border-blue-500/30">
              <p className="text-sm text-gray-400 mb-1">Min Protocols</p>
              <p className="text-xl font-bold text-white">{Number(constraints.min_protocols)}</p>
            </div>
            <div className="bg-orange-600/20 p-4 rounded-lg border border-orange-500/30">
              <p className="text-sm text-gray-400 mb-1">Max Volatility</p>
              <p className="text-xl font-bold text-white">{(Number(constraints.max_volatility) / 100).toFixed(0)}%</p>
            </div>
            <div className="bg-green-600/20 p-4 rounded-lg border border-green-500/30">
              <p className="text-sm text-gray-400 mb-1">Min Liquidity</p>
              <p className="text-xl font-bold text-white">{Number(constraints.min_liquidity).toLocaleString()}</p>
            </div>
          </div>
        ) : (
          <p className="text-gray-400">No constraints data available</p>
        )}
      </div>

      <div className="bg-black/30 backdrop-blur-md border border-purple-500/20 rounded-lg shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-4 text-white">Recent AI Decisions</h2>
        <p className="text-gray-400">No decisions yet</p>
      </div>
    </div>
  );
}


