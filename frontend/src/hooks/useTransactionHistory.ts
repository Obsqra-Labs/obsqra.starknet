import { useState, useEffect } from 'react';
import { useAccount } from '@starknet-react/core';

export interface Transaction {
  id: string;
  hash: string;
  type:
    | 'UPDATE_ALLOCATION'
    | 'SET_CONSTRAINTS'
    | 'ACCRUE_YIELDS'
    | 'DEPOSIT'
    | 'WITHDRAW'
    | 'AI_ORCHESTRATION'
    | 'UNKNOWN';
  status: 'pending' | 'confirmed' | 'failed';
  timestamp: number;
  details: any;
  error?: string;
}

const STORAGE_KEY = 'obsqra_transaction_history';
const MAX_HISTORY_SIZE = 50;

export function useTransactionHistory() {
  const { address } = useAccount();
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  // Load transactions from localStorage
  useEffect(() => {
    if (!address) return;
    
    try {
      const stored = localStorage.getItem(`${STORAGE_KEY}_${address}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        setTransactions(parsed);
      }
    } catch (error) {
      console.error('Failed to load transaction history:', error);
    }
  }, [address]);

  // Save transactions to localStorage
  const saveTransactions = (txs: Transaction[]) => {
    if (!address) {
      console.warn('⚠️ saveTransactions called but no address available');
      return;
    }
    
    try {
      const key = `${STORAGE_KEY}_${address}`;
      localStorage.setItem(key, JSON.stringify(txs));
      console.log('💾 Saved', txs.length, 'transactions to localStorage at key:', key);
      setTransactions(txs);
    } catch (error) {
      console.error('❌ Failed to save transaction history:', error);
    }
  };

  // Add a new transaction
  const addTransaction = (
    hash: string,
    type: Transaction['type'],
    details: any = {}
  ): string => {
    const id = `${hash}_${Date.now()}`;
    const newTx: Transaction = {
      id,
      hash,
      type,
      status: 'pending',
      timestamp: Date.now(),
      details,
    };

    console.log('📝 addTransaction called:', { id, hash, type, address });
    const updated = [newTx, ...transactions].slice(0, MAX_HISTORY_SIZE);
    console.log('📝 Updated transactions array:', updated);
    saveTransactions(updated);
    console.log('📝 Saved to localStorage with key:', `${STORAGE_KEY}_${address}`);
    return id;
  };

  // Update transaction status (read from localStorage to avoid stale state)
  const updateTransaction = (id: string, updates: Partial<Transaction>) => {
    if (!address) {
      console.warn('⚠️ updateTransaction called but no address available');
      return;
    }
    
    // Read fresh data from localStorage instead of relying on React state
    const key = `${STORAGE_KEY}_${address}`;
    const stored = localStorage.getItem(key);
    let allTransactions: Transaction[] = stored ? JSON.parse(stored) : [];
    
    console.log('📝 updateTransaction - read from localStorage:', allTransactions.length, 'txs');
    console.log('📝 updateTransaction - looking for ID:', id);
    console.log('📝 updateTransaction - stored txs:', allTransactions.map(tx => ({ id: tx.id, status: tx.status })));
    
    const txIndex = allTransactions.findIndex(tx => tx.id === id);
    if (txIndex === -1) {
      console.warn('⚠️ Transaction ID not found in localStorage! ID:', id);
      console.log('📝 Available IDs:', allTransactions.map(tx => tx.id));
      return;
    }
    
    const updated = allTransactions.map(tx =>
      tx.id === id ? { ...tx, ...updates } : tx
    );
    
    console.log('📝 updateTransaction - after update:', updated.map(tx => ({ id: tx.id, status: tx.status })));
    saveTransactions(updated);
  };

  // Mark transaction as confirmed
  const confirmTransaction = (id: string) => {
    console.log('🔄 confirmTransaction called with ID:', id);
    console.log('Current transactions (from state):', transactions);
    const found = transactions.find(tx => tx.id === id);
    if (!found) {
      console.warn('⚠️ Transaction with ID not found in state, reading from localStorage...');
    }
    updateTransaction(id, { status: 'confirmed' });
  };

  // Mark transaction as failed
  const failTransaction = (id: string, error: string) => {
    updateTransaction(id, { status: 'failed', error });
  };

  // Clear all transactions
  const clearHistory = () => {
    saveTransactions([]);
  };

  // Get transactions by status
  const getByStatus = (status: Transaction['status']) => {
    return transactions.filter(tx => tx.status === status);
  };

  // Get recent transactions (last N)
  const getRecent = (count: number = 10) => {
    return transactions.slice(0, count);
  };

  return {
    transactions,
    addTransaction,
    updateTransaction,
    confirmTransaction,
    failTransaction,
    clearHistory,
    getByStatus,
    getRecent,
    pendingCount: getByStatus('pending').length,
  };
}
