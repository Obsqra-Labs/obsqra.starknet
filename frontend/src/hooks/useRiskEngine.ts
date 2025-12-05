import { useContractRead, useContractWrite } from '@starknet-react/core';
import { useMemo } from 'react';
import { Abi } from 'starknet';

const RISK_ENGINE_ABI = [
  {
    type: 'function',
    name: 'calculate_risk_score',
    inputs: [
      { name: 'utilization', type: 'felt252' },
      { name: 'volatility', type: 'felt252' },
      { name: 'liquidity', type: 'felt252' },
      { name: 'audit_score', type: 'felt252' },
      { name: 'age_days', type: 'felt252' },
    ],
    outputs: [{ name: 'risk_score', type: 'felt252' }],
    stateMutability: 'view',
  },
] as Abi;

export function useRiskEngine(contractAddress: string) {
  const { data: riskScore } = useContractRead({
    functionName: 'calculate_risk_score',
    args: [5000, 2000, 0, 95, 1000], // Example args
    abi: RISK_ENGINE_ABI,
    address: contractAddress,
  });

  const { write: calculateAllocation } = useContractWrite({
    calls: useMemo(() => {
      if (!contractAddress) return [];
      return [
        {
          contractAddress,
          entrypoint: 'calculate_allocation',
          calldata: [],
        },
      ];
    }, [contractAddress]),
  });

  return {
    riskScore,
    calculateAllocation,
  };
}

