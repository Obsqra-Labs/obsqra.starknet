import { useReadContract, useAccount } from '@starknet-react/core';
import { useMemo, useState } from 'react';
import { Abi } from 'starknet';

const DAO_CONSTRAINT_ABI = [
  {
    type: 'function',
    name: 'get_constraints',
    inputs: [],
    outputs: [
      { name: 'max_single_protocol', type: 'felt252' },
      { name: 'min_protocols', type: 'felt252' },
      { name: 'max_volatility', type: 'felt252' },
      { name: 'min_liquidity', type: 'felt252' },
    ],
    stateMutability: 'view',
  },
  {
    type: 'function',
    name: 'set_constraints',
    inputs: [
      { name: 'max_single', type: 'felt252' },
      { name: 'min_diversification', type: 'felt252' },
      { name: 'max_volatility', type: 'felt252' },
      { name: 'min_liquidity', type: 'felt252' },
    ],
    outputs: [],
    stateMutability: 'external',
  },
  {
    type: 'function',
    name: 'validate_allocation',
    inputs: [
      { name: 'aave_pct', type: 'felt252' },
      { name: 'lido_pct', type: 'felt252' },
      { name: 'compound_pct', type: 'felt252' },
    ],
    outputs: [{ name: 'is_valid', type: 'bool' }],
    stateMutability: 'view',
  },
] as Abi;

export interface DAOConstraints {
  max_single_protocol: bigint;
  min_protocols: bigint;
  max_volatility: bigint;
  min_liquidity: bigint;
}

export function useDAOConstraints(contractAddress: string) {
  const { account } = useAccount();
  const [isUpdating, setIsUpdating] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  // Read current constraints
  const { data: constraints, isLoading, refetch } = useReadContract({
    functionName: 'get_constraints',
    args: [],
    abi: DAO_CONSTRAINT_ABI,
    address: contractAddress || undefined,
    watch: true,
    enabled: !!contractAddress,
  });

  // Parse constraints data
  const parsedConstraints = useMemo(() => {
    if (!constraints || !Array.isArray(constraints)) return null;
    return {
      max_single_protocol: BigInt(constraints[0]?.toString() || 0),
      min_protocols: BigInt(constraints[1]?.toString() || 0),
      max_volatility: BigInt(constraints[2]?.toString() || 0),
      min_liquidity: BigInt(constraints[3]?.toString() || 0),
    };
  }, [constraints]);

  // Set constraints function (owner only)
  const setConstraints = async (
    maxSingle: number,
    minDiversification: number,
    maxVolatility: number,
    minLiquidity: number
  ) => {
    if (!account || !contractAddress) {
      throw new Error('Wallet not connected or contract address missing');
    }
    
    setIsUpdating(true);
    try {
      const result = await account.execute([{
        contractAddress,
        entrypoint: 'set_constraints',
        calldata: [
          maxSingle.toString(),
          minDiversification.toString(),
          maxVolatility.toString(),
          minLiquidity.toString(),
        ],
      }]);
      
      await account.waitForTransaction(result.transaction_hash);
      await refetch();
      
      return result.transaction_hash;
    } catch (error) {
      console.error('Failed to set constraints:', error);
      throw error;
    } finally {
      setIsUpdating(false);
    }
  };

  // Validate allocation against constraints
  const validateAllocation = async (nostra: number, zklend: number, ekubo: number) => {
    if (!contractAddress) {
      throw new Error('Contract address missing');
    }
    
    setIsValidating(true);
    try {
      // Use read contract to validate
      const result = await account?.provider.callContract({
        contractAddress,
        entrypoint: 'validate_allocation',
        calldata: [nostra.toString(), zklend.toString(), ekubo.toString()],
      });
      
      return result && result.length > 0 && result[0] !== '0';
    } catch (error) {
      console.error('Failed to validate allocation:', error);
      return false;
    } finally {
      setIsValidating(false);
    }
  };

  return {
    constraints: parsedConstraints,
    isLoading,
    setConstraints,
    isUpdating,
    validateAllocation,
    isValidating,
    refetch,
  };
}

