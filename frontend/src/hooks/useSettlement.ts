'use client';

import { useAccount } from '@starknet-react/core';
import { Contract, AccountInterface } from 'starknet';
import { useState, useCallback } from 'react';
import { getConfig } from '@/lib/config';

// StrategyRouter V2 ABI for update_allocation - 2 protocols: JediSwap and Ekubo
const STRATEGY_ROUTER_V2_ABI = [
  {
    type: 'function',
    name: 'update_allocation',
    inputs: [
      { name: 'jediswap_pct', type: 'core::felt252' },
      { name: 'ekubo_pct', type: 'core::felt252' },
    ],
    outputs: [],
    stateMutability: 'external',
  },
];

interface AllocationData {
  jediswap: number;
  ekubo: number;
}

interface SettlementResult {
  txHash: string;
  status: 'pending' | 'confirmed' | 'failed';
  error: string | null;
}

export function useSettlement() {
  const { account, address } = useAccount();

  const [isLoading, setIsLoading] = useState(false);
  const [lastTxHash, setLastTxHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SettlementResult | null>(null);

  const updateAllocation = useCallback(
    async (allocation: AllocationData) => {
      if (!account || !address) {
        setError('Wallet not connected');
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const config = getConfig();
        const strategyRouterAddress = config.strategyRouterAddress;

        if (!strategyRouterAddress) {
          throw new Error('Strategy Router address not configured');
        }

        // Convert percentages to basis points (multiply by 100 for u256)
        const jediPct = Math.round(allocation.jediswap * 100);
        const ekPct = Math.round(allocation.ekubo * 100);

        // Verify percentages sum to 10000 (100%)
        if (jediPct + ekPct !== 10000) {
          throw new Error(
            `Allocation must sum to 100%. Got ${jediPct / 100}% + ${ekPct / 100}% = ${(jediPct + ekPct) / 100}%`
          );
        }

        // Create contract instance using account (has provider)
        const contract = new Contract(
          STRATEGY_ROUTER_V2_ABI,
          strategyRouterAddress,
          account as unknown as AccountInterface
        );

        // Call update_allocation on the contract with JediSwap and Ekubo percentages
        console.log('📤 Calling update_allocation on contract with values:', { jediPct, ekPct });
        const response = await contract.invoke('update_allocation', [jediPct, ekPct]);

        const txHash = response.transaction_hash;
        setLastTxHash(txHash);
        
        console.log('✅ Transaction sent:', txHash);
        
        // Return pending status - will be confirmed when transaction settles
        setResult({
          txHash,
          status: 'pending',
          error: null,
        });

        return {
          txHash,
          status: 'pending' as const,
          error: null,
        };
      } catch (err) {
        let errorMessage = 'Settlement failed';
        
        // Parse Starknet/Argent errors for better user feedback
        if (err instanceof Error) {
          errorMessage = err.message;
          
          // Check for authorization errors
          if (errorMessage.includes('Unauthorized') || errorMessage.includes('ENTRYPOINT_FAILED')) {
            errorMessage = 'Unauthorized: Your account does not have permission to update allocation. The contract may require admin/owner privileges.';
          } else if (errorMessage.includes('argent/multicall-failed')) {
            errorMessage = 'Transaction failed: The contract rejected the allocation update. This may be due to insufficient permissions or contract restrictions.';
          } else if (errorMessage.includes('multicall')) {
            errorMessage = 'Transaction failed: The multicall operation was rejected by the contract.';
          }
        } else if (typeof err === 'object' && err !== null) {
          // Handle Starknet error objects
          const errObj = err as any;
          if (errObj.message) {
            errorMessage = errObj.message;
          } else if (errObj.reason) {
            errorMessage = `Contract error: ${errObj.reason}`;
          }
        }
        
        console.error('❌ Settlement error:', err);
        console.error('❌ Parsed error message:', errorMessage);
        setError(errorMessage);
        setResult({
          txHash: lastTxHash || '',
          status: 'failed',
          error: errorMessage,
        });
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [account, address, lastTxHash]
  );

  return {
    updateAllocation,
    isLoading,
    lastTxHash,
    error,
    result,
    isConnected: !!account && !!address,
  };
}

