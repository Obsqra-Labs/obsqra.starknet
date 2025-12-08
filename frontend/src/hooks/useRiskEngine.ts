'use client';

import { useAccount } from '@starknet-react/core';
import { useMemo, useState, useCallback } from 'react';
import { Contract, Abi } from 'starknet';
import { getContractAddress } from '@/lib/config';

/**
 * Risk metrics for protocol assessment
 * All values are percentages (0-100) or basis points where specified
 */
export interface ProtocolMetrics {
  utilization: number; // 0-100: % of available liquidity being used
  volatility: number; // 0-100: price volatility score
  liquidity: number; // 0-3: liquidity category (0=High, 1=Medium, 2=Low, 3=VeryLow)
  auditScore: number; // 0-100: audit/security score
  ageDays: number; // days since protocol launch
}

/**
 * Risk score output from Cairo contract
 * Range: 5-95 (clipped to avoid extremes)
 */
export interface RiskScore {
  score: number;
  category: 'low' | 'medium' | 'high';
  description: string;
}

/**
 * Allocation output from Cairo contract
 * Basis points: 10000 = 100%
 */
export interface AllocationResult {
  jediswapPct: number;  // JediSwap allocation %
  ekuboPct: number;     // Ekubo allocation %
  proofHash?: string;   // Optional: SHARP proof hash
}

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
  {
    type: 'function',
    name: 'calculate_allocation',
    inputs: [
      { name: 'jediswap_risk', type: 'felt252' },
      { name: 'ekubo_risk', type: 'felt252' },
      { name: 'jediswap_apy', type: 'felt252' },
      { name: 'ekubo_apy', type: 'felt252' },
    ],
    outputs: [
      { name: 'jediswap_pct', type: 'felt252' },
      { name: 'ekubo_pct', type: 'felt252' },
    ],
    stateMutability: 'view',
  },
] as Abi;

const getRiskCategory = (score: number): RiskScore['category'] => {
  if (score < 30) return 'low';
  if (score < 70) return 'medium';
  return 'high';
};

const getRiskDescription = (score: number): string => {
  if (score < 30) return 'Low risk protocol - Safe for allocation';
  if (score < 70) return 'Medium risk - Consider allocation limits';
  return 'High risk - Use small allocation only';
};

export interface UseRiskEngineReturn {
  // Risk scoring
  calculateRiskScore: (metrics: ProtocolMetrics) => Promise<RiskScore | null>;
  lastRiskScore: RiskScore | null;
  
  // Allocation computation (2 protocols: JediSwap + Ekubo)
  calculateAllocation: (
    jediswapMetrics: ProtocolMetrics,
    ekuboMetrics: ProtocolMetrics,
    apys: { jediswap: number; ekubo: number }
  ) => Promise<AllocationResult | null>;
  lastAllocation: AllocationResult | null;
  
  // State
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
}

export function useRiskEngine(contractAddress?: `0x${string}`): UseRiskEngineReturn {
  const { account } = useAccount();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRiskScore, setLastRiskScore] = useState<RiskScore | null>(null);
  const [lastAllocation, setLastAllocation] = useState<AllocationResult | null>(null);

  // Use provided address or get from config
  const finalContractAddress = useMemo(() => {
    if (contractAddress) return contractAddress;
    return getContractAddress('riskEngine');
  }, [contractAddress]);

  const clearError = useCallback(() => setError(null), []);

  // Calculate risk score for a single protocol via Cairo contract
  const calculateRiskScore = useCallback(
    async (metrics: ProtocolMetrics): Promise<RiskScore | null> => {
      if (!finalContractAddress || !account) {
        setError('Risk Engine contract address or account not configured');
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Call the Risk Engine contract's calculate_risk_score function
        // @ts-ignore - starknet-react types
        const provider = account.provider || (account as any).provider;
        
        if (!provider) {
          throw new Error('No provider available');
        }

        const contract = new Contract(
          RISK_ENGINE_ABI as any,
          finalContractAddress,
          provider as any
        );

        const result = await contract.call('calculate_risk_score', [
          metrics.utilization,  // felt252
          metrics.volatility,   // felt252
          metrics.liquidity,    // felt252
          metrics.auditScore,   // felt252
          metrics.ageDays,      // felt252
        ]);

        const score = typeof result === 'bigint' ? Number(result) : Array.isArray(result) ? Number((result as any[])[0]) : Number(result);
        
        const riskScore: RiskScore = {
          score: Math.min(95, Math.max(5, score)),
          category: getRiskCategory(score),
          description: getRiskDescription(score),
        };

        console.log(`✅ Risk score calculated:`, riskScore);
        setLastRiskScore(riskScore);
        return riskScore;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to calculate risk score';
        setError(errorMsg);
        console.error('❌ Risk calculation error:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [finalContractAddress, account]
  );

  // Calculate optimal allocation across 2 protocols (JediSwap + Ekubo) via Cairo contract
  const calculateAllocation = useCallback(
    async (
      jediswapMetrics: ProtocolMetrics,
      ekuboMetrics: ProtocolMetrics,
      apys: { jediswap: number; ekubo: number }
    ): Promise<AllocationResult | null> => {
      if (!finalContractAddress || !account) {
        setError('Risk Engine contract address or account not configured');
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Get risk scores for each protocol
        const jediswapRisk = await calculateRiskScore(jediswapMetrics);
        const ekuboRisk = await calculateRiskScore(ekuboMetrics);

        if (!jediswapRisk || !ekuboRisk) {
          throw new Error('Failed to calculate protocol risk scores');
        }

        console.log('📊 Calling Risk Engine contract with:',  {
          jediswap_risk: jediswapRisk.score,
          ekubo_risk: ekuboRisk.score,
          jediswap_apy: apys.jediswap,
          ekubo_apy: apys.ekubo,
        });

        // Call the Risk Engine contract's calculate_allocation function
        // @ts-ignore - starknet-react types
        const provider = account.provider || (account as any).provider;
        
        if (!provider) {
          throw new Error('No provider available');
        }

        const contract = new Contract(
          RISK_ENGINE_ABI as any,
          finalContractAddress,
          provider as any
        );

        const result = await contract.call('calculate_allocation', [
          jediswapRisk.score,   // jediswap_risk (felt252)
          ekuboRisk.score,      // ekubo_risk (felt252)
          apys.jediswap,        // jediswap_apy (felt252)
          apys.ekubo,           // ekubo_apy (felt252)
        ]);

        // Result is tuple (jediswap_pct, ekubo_pct)
        const [jediswapPct, ekuboPct] = Array.isArray(result) 
          ? (result as any[])
          : [(result as any)[0], (result as any)[1]];

        const allocation: AllocationResult = {
          jediswapPct: typeof jediswapPct === 'bigint' ? Number(jediswapPct) : Number(jediswapPct),
          ekuboPct: typeof ekuboPct === 'bigint' ? Number(ekuboPct) : Number(ekuboPct),
        };

        console.log('✅ Allocation from Risk Engine contract:', allocation);
        setLastAllocation(allocation);
        return allocation;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to calculate allocation';
        setError(errorMsg);
        console.error('❌ Allocation calculation error:', err);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [finalContractAddress, account, calculateRiskScore]
  );

  return {
    calculateRiskScore,
    lastRiskScore,
    calculateAllocation,
    lastAllocation,
    isLoading,
    error,
    clearError,
  };
}
