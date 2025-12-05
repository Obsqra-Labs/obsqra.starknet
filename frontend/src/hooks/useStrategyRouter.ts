import { useReadContract, useAccount, useContract } from '@starknet-react/core';
import { useMemo, useState } from 'react';
import { Abi, Contract } from 'starknet';

const STRATEGY_ROUTER_ABI = [
  {
    type: 'function',
    name: 'get_allocation',
    inputs: [],
    outputs: [
      { name: 'aave_pct', type: 'felt252' },
      { name: 'lido_pct', type: 'felt252' },
      { name: 'compound_pct', type: 'felt252' },
    ],
    stateMutability: 'view',
  },
  {
    type: 'function',
    name: 'update_allocation',
    inputs: [
      { name: 'aave_pct', type: 'felt252' },
      { name: 'lido_pct', type: 'felt252' },
      { name: 'compound_pct', type: 'felt252' },
    ],
    outputs: [],
    stateMutability: 'external',
  },
  {
    type: 'function',
    name: 'accrue_yields',
    inputs: [],
    outputs: [],
    stateMutability: 'external',
  },
] as Abi;

export interface Allocation {
  nostra_pct: bigint;
  zklend_pct: bigint;
  ekubo_pct: bigint;
}

export function useStrategyRouter(contractAddress: string) {
  const { account } = useAccount();
  const [isUpdating, setIsUpdating] = useState(false);
  const [isAccruing, setIsAccruing] = useState(false);

  // Read current allocation
  const { data: allocation, isLoading, refetch } = useReadContract({
    functionName: 'get_allocation',
    args: [],
    abi: STRATEGY_ROUTER_ABI,
    address: contractAddress || undefined,
    watch: true,
    enabled: !!contractAddress,
  });

  // Parse allocation data
  const parsedAllocation = useMemo(() => {
    if (!allocation || !Array.isArray(allocation)) return null;
    return {
      nostra_pct: BigInt(allocation[0]?.toString() || 0),
      zklend_pct: BigInt(allocation[1]?.toString() || 0),
      ekubo_pct: BigInt(allocation[2]?.toString() || 0),
    };
  }, [allocation]);

  // Update allocation function
  const updateAllocation = async (nostra: number, zklend: number, ekubo: number) => {
    if (!account || !contractAddress) {
      throw new Error('Wallet not connected or contract address missing');
    }
    
    setIsUpdating(true);
    try {
      const result = await account.execute([{
        contractAddress,
        entrypoint: 'update_allocation',
        calldata: [nostra.toString(), zklend.toString(), ekubo.toString()],
      }]);
      
      // Wait for transaction confirmation
      await account.waitForTransaction(result.transaction_hash);
      
      // Refetch allocation data
      await refetch();
      
      return result.transaction_hash;
    } catch (error) {
      console.error('Failed to update allocation:', error);
      throw error;
    } finally {
      setIsUpdating(false);
    }
  };

  // Accrue yields function
  const accrueYields = async () => {
    if (!account || !contractAddress) {
      throw new Error('Wallet not connected or contract address missing');
    }
    
    setIsAccruing(true);
    try {
      const result = await account.execute([{
        contractAddress,
        entrypoint: 'accrue_yields',
        calldata: [],
      }]);
      
      await account.waitForTransaction(result.transaction_hash);
      return result.transaction_hash;
    } catch (error) {
      console.error('Failed to accrue yields:', error);
      throw error;
    } finally {
      setIsAccruing(false);
    }
  };

  return {
    allocation: parsedAllocation,
    isLoading,
    updateAllocation,
    isUpdating,
    accrueYields,
    isAccruing,
    refetch,
  };
}

