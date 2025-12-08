'use client';

import { useMemo, useState, useCallback } from 'react';
import { getContractAddress } from '@/lib/config';

/**
 * Risk metrics for protocol assessment
 */
export interface ProtocolMetrics {
  utilization: number;
  volatility: number;
  liquidity: number;
  auditScore: number;
  ageDays: number;
}

/**
 * Risk score from backend Risk Engine
 */
export interface RiskScore {
  score: number;
  category: 'low' | 'medium' | 'high';
  description: string;
}

/**
 * Allocation from backend Risk Engine
 */
export interface AllocationResult {
  jediswapPct: number;
  ekuboPct: number;
}

export interface UseRiskEngineBackendReturn {
  // Risk scoring
  calculateRiskScore: (metrics: ProtocolMetrics) => Promise<RiskScore | null>;
  lastRiskScore: RiskScore | null;
  
  // Allocation computation
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

export function useRiskEngineBackend(): UseRiskEngineBackendReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRiskScore, setLastRiskScore] = useState<RiskScore | null>(null);
  const [lastAllocation, setLastAllocation] = useState<AllocationResult | null>(null);

  const backendUrl = useMemo(() => {
    if (typeof window === 'undefined') return '';
    return process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001';
  }, []);

  const clearError = useCallback(() => setError(null), []);

  // Calculate risk score via backend
  const calculateRiskScore = useCallback(
    async (metrics: ProtocolMetrics): Promise<RiskScore | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${backendUrl}/api/v1/risk-engine/calculate-risk`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            utilization: metrics.utilization,
            volatility: metrics.volatility,
            liquidity: metrics.liquidity,
            audit_score: metrics.auditScore,
            age_days: metrics.ageDays,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Risk calculation failed: ${response.statusText}`);
        }

        const data = await response.json();
        
        const riskScore: RiskScore = {
          score: data.score,
          category: data.category,
          description: data.description,
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
    [backendUrl]
  );

  // Calculate allocation via backend
  const calculateAllocation = useCallback(
    async (
      jediswapMetrics: ProtocolMetrics,
      ekuboMetrics: ProtocolMetrics,
      apys: { jediswap: number; ekubo: number }
    ): Promise<AllocationResult | null> => {
      setIsLoading(true);
      setError(null);

      try {
        // Get risk scores for each protocol
        const jediswapRisk = await calculateRiskScore(jediswapMetrics);
        const ekuboRisk = await calculateRiskScore(ekuboMetrics);

        if (!jediswapRisk || !ekuboRisk) {
          throw new Error('Failed to calculate protocol risk scores');
        }

        console.log('📊 Calling backend Risk Engine with:', {
          jediswap_risk: jediswapRisk.score,
          ekubo_risk: ekuboRisk.score,
          jediswap_apy: apys.jediswap,
          ekubo_apy: apys.ekubo,
        });

        const response = await fetch(`${backendUrl}/api/v1/risk-engine/calculate-allocation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            jediswap_risk: jediswapRisk.score,
            ekubo_risk: ekuboRisk.score,
            jediswap_apy: apys.jediswap,
            ekubo_apy: apys.ekubo,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Allocation calculation failed: ${response.statusText}`);
        }

        const data = await response.json();
        
        const allocation: AllocationResult = {
          jediswapPct: data.jediswap_pct,
          ekuboPct: data.ekubo_pct,
        };

        console.log('✅ Allocation from backend Risk Engine:', allocation);
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
    [backendUrl, calculateRiskScore]
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

