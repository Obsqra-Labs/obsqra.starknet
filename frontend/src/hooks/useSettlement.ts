'use client';

import { useAccount } from '@starknet-react/core';
import { Contract, AccountInterface, RpcProvider } from 'starknet';
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
  status: 'pending' | 'success' | 'confirmed' | 'failed';
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

        // Check authorization BEFORE calling - update_allocation requires owner or RiskEngine
        // Owner and RiskEngine addresses from deployment config
        const ownerAddress = '0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d';
        const riskEngineAddress = '0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80';
        const userAddress = (account.address || '').toLowerCase();
        
        if (userAddress !== ownerAddress.toLowerCase() && userAddress !== riskEngineAddress.toLowerCase()) {
          throw new Error(
            `❌ Unauthorized: update_allocation requires owner or RiskEngine authorization.\n\n` +
            `Your address: ${account.address}\n` +
            `Owner: ${ownerAddress}\n` +
            `RiskEngine: ${riskEngineAddress}\n\n` +
            `Only the owner or RiskEngine can update allocations. Regular users should use the RiskEngine backend to propose allocation changes.`
          );
        }
        
        // Call update_allocation on the contract with JediSwap and Ekubo percentages
        console.log('📤 Calling update_allocation on contract with values:', { jediPct, ekPct });
        
        const response = await contract.invoke('update_allocation', [jediPct, ekPct]);

        const txHash = response.transaction_hash;
        setLastTxHash(txHash);
        
        console.log('✅ Transaction sent:', txHash);
        
        // Wait for transaction to be confirmed
        try {
          const config = getConfig();
          const provider = new RpcProvider({ nodeUrl: config.rpcUrl });
          console.log('⏳ Waiting for transaction confirmation...');
          await provider.waitForTransaction(txHash, { retryInterval: 2000 });
          console.log('✅ Transaction confirmed:', txHash);
        } catch (waitError) {
          console.warn('⚠️ Could not wait for transaction confirmation:', waitError);
          // Continue anyway - transaction might still be processing
        }
        
        // Return success status
        setResult({
          txHash,
          status: 'success',
          error: null,
        });

        return {
          txHash,
          status: 'success' as const,
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

