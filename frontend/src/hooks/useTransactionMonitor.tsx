'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { RpcProvider } from 'starknet';
import { getConfig } from '@/lib/config';

export interface TransactionStatus {
  hash: string;
  status: 'pending' | 'succeeded' | 'failed' | 'not_found';
  blockNumber?: number;
  blockTimestamp?: number;
  gasUsed?: string;
  error?: string;
  confirmations: number;
  explorerUrl: string;
}

interface MonitoringOptions {
  pollIntervalMs?: number;
  maxPollAttempts?: number;
  rpcUrl?: string;
  networkName?: 'sepolia' | 'mainnet';
}

const DEFAULT_POLL_INTERVAL = 3000; // 3 seconds
const DEFAULT_MAX_POLLS = 40; // ~2 minutes with 3s interval
const DEFAULT_RPC_URL = getConfig().rpcUrl;

const EXPLORER_URLS: Record<string, string> = {
  sepolia: 'https://starkscan.co/tx',
  mainnet: 'https://starkscan.co/tx',
};

/**
 * Hook to monitor transaction status on-chain
 * Polls block explorer / RPC until transaction is confirmed or times out
 */
export function useTransactionMonitor(
  txHash?: string,
  options: MonitoringOptions = {}
) {
  const {
    pollIntervalMs = DEFAULT_POLL_INTERVAL,
    maxPollAttempts = DEFAULT_MAX_POLLS,
    rpcUrl = DEFAULT_RPC_URL,
    networkName = 'sepolia',
  } = options;

  const [status, setStatus] = useState<TransactionStatus | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [pollCount, setPollCount] = useState(0);

  const explorerUrl = `${EXPLORER_URLS[networkName]}/${txHash}?network=${networkName}`;

  const pollTransactionStatus = useCallback(async (): Promise<TransactionStatus | null> => {
    if (!txHash) return null;

    try {
      const provider = new RpcProvider({ nodeUrl: rpcUrl });

      // Get transaction receipt
      const receipt = await provider.getTransactionReceipt(txHash);

      if (!receipt) {
        return {
          hash: txHash,
          status: 'not_found',
          confirmations: 0,
          explorerUrl,
        };
      }

      // Determine transaction status
      let transactionStatus: 'succeeded' | 'failed' | 'pending' = 'pending';
      const executionStatus = (receipt as any).execution_status;
      const finalityStatus = (receipt as any).finality_status;
      
      if (executionStatus === 'SUCCEEDED' || finalityStatus === 'ACCEPTED_ON_L2' || finalityStatus === 'ACCEPTED_ON_L1') {
        transactionStatus = 'succeeded';
      } else if (executionStatus === 'REVERTED' || finalityStatus === 'REJECTED') {
        transactionStatus = 'failed';
      }

      // Get current block number for confirmation count
      const blockNumber = await provider.getBlockNumber();
      const receiptBlockNumber = (receipt as any).block_number || 0;
      
      const confirmations = Math.max(0, blockNumber - (typeof receiptBlockNumber === 'number' ? receiptBlockNumber : 0));

      return {
        hash: txHash,
        status: transactionStatus,
        blockNumber: typeof receiptBlockNumber === 'number' ? receiptBlockNumber : undefined,
        blockTimestamp: (receipt as any).block_timestamp,
        gasUsed: (receipt as any).actual_fee?.amount?.toString(),
        confirmations,
        explorerUrl,
      };
    } catch (error) {
      console.error('Error polling transaction:', error);
      return {
        hash: txHash,
        status: 'pending',
        confirmations: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
        explorerUrl,
      };
    }
  }, [txHash, rpcUrl, explorerUrl]);

  useEffect(() => {
    if (!txHash || !isMonitoring) return;

    let pollIntervalTimer: NodeJS.Timeout | null = null;

    const performPoll = async () => {
      if (pollCount >= maxPollAttempts) {
        setStatus(prev => prev ? { ...prev, status: 'pending' as const } : null);
        setIsMonitoring(false);
        return;
      }

      const txStatus = await pollTransactionStatus();
      if (txStatus) {
        setStatus(txStatus);
        setPollCount(prev => prev + 1);

        // Stop polling if transaction is confirmed or failed
        if (txStatus.status !== 'pending' && txStatus.status !== 'not_found') {
          setIsMonitoring(false);
          return;
        }
      }
    };

    // Perform initial poll immediately
    performPoll();

    // Then poll at regular intervals
    pollIntervalTimer = setInterval(performPoll, pollIntervalMs);

    return () => {
      if (pollIntervalTimer) {
        clearInterval(pollIntervalTimer);
      }
    };
  }, [txHash, isMonitoring, pollCount, maxPollAttempts, pollIntervalMs, pollTransactionStatus]);

  const startMonitoring = useCallback(() => {
    if (txHash) {
      setIsMonitoring(true);
      setPollCount(0);
      setStatus({
        hash: txHash,
        status: 'pending',
        confirmations: 0,
        explorerUrl,
      });
    }
  }, [txHash, explorerUrl]);

  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
  }, []);

  const resetMonitoring = useCallback(() => {
    setIsMonitoring(false);
    setPollCount(0);
    setStatus(null);
  }, []);

  return {
    status,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    resetMonitoring,
    pollCount,
  };
}

/**
 * Helper component to display transaction status
 */
export function TransactionStatusBadge({ status }: { status: TransactionStatus | null }) {
  if (!status) {
    return null;
  }

  const statusColors: Record<TransactionStatus['status'], string> = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    succeeded: 'bg-green-500/20 text-green-400 border-green-500/30',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30',
    not_found: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  const statusIcon: Record<TransactionStatus['status'], string> = {
    pending: '⏳',
    succeeded: '✓',
    failed: '✗',
    not_found: '?',
  };

  const statusLabel: Record<TransactionStatus['status'], string> = {
    pending: 'Pending',
    succeeded: 'Confirmed',
    failed: 'Failed',
    not_found: 'Not Found',
  };

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-sm ${statusColors[status.status]}`}>
      <span>{statusIcon[status.status]}</span>
      <span>{statusLabel[status.status]}</span>
      {status.confirmations > 0 && (
        <span className="text-xs opacity-75">({status.confirmations} blocks)</span>
      )}
    </div>
  );
}
