'use client';

import { useTransactionHistory, Transaction } from '@/hooks/useTransactionHistory';
import { useState } from 'react';

const TX_TYPE_LABELS: Record<Transaction['type'], string> = {
  UPDATE_ALLOCATION: 'Update Allocation',
  SET_CONSTRAINTS: 'Set Constraints',
  ACCRUE_YIELDS: 'Accrue Yields',
  DEPOSIT: 'Deposit STRK',
  WITHDRAW: 'Withdraw STRK',
  AI_ORCHESTRATION: 'AI Orchestration',
  UNKNOWN: 'Unknown',
};

const STATUS_COLORS = {
  pending: 'text-yellow-400 bg-yellow-400/10',
  confirmed: 'text-green-400 bg-green-400/10',
  failed: 'text-red-400 bg-red-400/10',
};

function TransactionRow({ tx }: { tx: Transaction }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const formatTime = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return `${seconds}s ago`;
  };

  const formatHash = (hash: string) => {
    return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
  };

  const openInVoyager = () => {
    window.open(`https://sepolia.voyager.online/tx/${tx.hash}`, '_blank');
  };

  return (
    <div className="border border-purple-500/20 rounded-lg p-4 hover:border-purple-500/40 transition">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[tx.status]}`}>
            {tx.status}
          </span>
          <span className="text-sm font-medium text-gray-200">
            {TX_TYPE_LABELS[tx.type]}
          </span>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">
            {formatTime(tx.timestamp)}
          </span>
          <button
            onClick={openInVoyager}
            className="text-xs text-blue-400 hover:text-blue-300 transition"
          >
            {formatHash(tx.hash)} ↗
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-gray-200 transition"
          >
            {isExpanded ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-purple-500/20">
          <div className="text-sm text-gray-300 space-y-2">
            <div>
              <span className="text-gray-400">Transaction Hash:</span>
              <div className="font-mono text-xs break-all text-blue-400">{tx.hash}</div>
            </div>
            
            {tx.details && Object.keys(tx.details).length > 0 && (
              <div>
                <span className="text-gray-400">Details:</span>
                <pre className="mt-1 p-2 bg-black/30 rounded text-xs overflow-x-auto">
                  {JSON.stringify(tx.details, null, 2)}
                </pre>
              </div>
            )}
            
            {tx.error && (
              <div>
                <span className="text-red-400">Error:</span>
                <div className="text-xs text-red-300 mt-1">{tx.error}</div>
              </div>
            )}
            
            <div className="text-xs text-gray-400">
              {new Date(tx.timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function TransactionHistory() {
  const { transactions, pendingCount, clearHistory } = useTransactionHistory();
  const [filter, setFilter] = useState<Transaction['status'] | 'all'>('all');

  const filteredTransactions = filter === 'all' 
    ? transactions 
    : transactions.filter(tx => tx.status === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Transaction History</h2>
        
        {transactions.length > 0 && (
          <button
            onClick={clearHistory}
            className="text-sm text-red-400 hover:text-red-300 transition"
          >
            Clear History
          </button>
        )}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {(['all', 'pending', 'confirmed', 'failed'] as const).map((status) => {
          const count = status === 'all' 
            ? transactions.length 
            : transactions.filter(tx => tx.status === status).length;
          
          return (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                filter === status
                  ? 'bg-purple-600 text-white'
                  : 'bg-purple-600/20 text-gray-300 hover:bg-purple-600/30'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
              {count > 0 && ` (${count})`}
            </button>
          );
        })}
      </div>

      {/* Transaction list */}
      {filteredTransactions.length > 0 ? (
        <div className="space-y-3">
          {filteredTransactions.map((tx) => (
            <TransactionRow key={tx.id} tx={tx} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          {filter === 'all' ? (
            <>
              <div className="text-4xl mb-4">📜</div>
              <p>No transactions yet</p>
              <p className="text-sm mt-2">Your transaction history will appear here</p>
            </>
          ) : (
            <p>No {filter} transactions</p>
          )}
        </div>
      )}

      {pendingCount > 0 && (
        <div className="text-sm text-yellow-400 flex items-center gap-2 justify-center">
          <div className="animate-spin">⏳</div>
          {pendingCount} transaction{pendingCount > 1 ? 's' : ''} pending...
        </div>
      )}
    </div>
  );
}
