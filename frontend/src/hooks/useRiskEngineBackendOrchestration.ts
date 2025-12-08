'use client';

import { useState, useCallback } from 'react';
import { getConfig } from '@/lib/config';

/**
 * Protocol metrics for backend orchestration
 */
export interface ProtocolMetrics {
  utilization: number; // 0-10000 basis points
  volatility: number;   // 0-10000 basis points
  liquidity: number;    // 0-3 categorical
  audit_score: number;  // 0-100
  age_days: number;     // days
}

/**
 * Allocation decision from backend (reflecting on-chain state)
 */
export interface AllocationDecision {
  decision_id: number;
  block_number: number;
  timestamp: number;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  jediswap_apy: number;
  ekubo_apy: number;
  rationale_hash: string;
  strategy_router_tx: string;
  message: string;
}

interface UseRiskEngineBackendOrchestrationReturn {
  proposeAndExecuteAllocation: (
    jediswapMetrics: ProtocolMetrics,
    ekuboMetrics: ProtocolMetrics
  ) => Promise<AllocationDecision | null>;
  getLatestDecision: () => Promise<AllocationDecision | null>;
  isLoading: boolean;
  error: string | null;
  clearError: () => void;
}

/**
 * Hook to orchestrate AI allocation via backend API
 * 
 * This uses the backend endpoint instead of calling the contract directly from the browser.
 * The backend properly handles Cairo struct serialization via starknet.py.
 * 
 * Flow:
 * 1. Frontend sends metrics to backend via HTTP
 * 2. Backend calls RiskEngine.propose_and_execute_allocation on-chain (via frontend wallet OR backend account)
 * 3. Backend reads the on-chain decision and returns it
 * 4. Frontend displays the result
 */
export function useRiskEngineBackendOrchestration(): UseRiskEngineBackendOrchestrationReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const proposeAndExecuteAllocation = useCallback(
    async (
      jediswapMetrics: ProtocolMetrics,
      ekuboMetrics: ProtocolMetrics
    ): Promise<AllocationDecision | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const config = getConfig();
        const backendUrl = config.backendUrl;

        if (!backendUrl) {
          throw new Error('Backend URL not configured');
        }

        console.log('🤖 Backend Orchestration: Proposing and executing allocation...');
        console.log('📊 JediSwap metrics:', jediswapMetrics);
        console.log('📊 Ekubo metrics:', ekuboMetrics);

        // Call backend orchestration endpoint
        // The backend will:
        // 1. Validate metrics
        // 2. Call propose_and_execute_allocation on RiskEngine (via user wallet or backend account)
        // 3. Read the on-chain decision
        // 4. Return the decision data
        const response = await fetch(`${backendUrl}/api/risk-engine/orchestrate-allocation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            jediswap_metrics: {
              utilization: jediswapMetrics.utilization,
              volatility: jediswapMetrics.volatility,
              liquidity: jediswapMetrics.liquidity,
              audit_score: jediswapMetrics.audit_score,
              age_days: jediswapMetrics.age_days,
            },
            ekubo_metrics: {
              utilization: ekuboMetrics.utilization,
              volatility: ekuboMetrics.volatility,
              liquidity: ekuboMetrics.liquidity,
              audit_score: ekuboMetrics.audit_score,
              age_days: ekuboMetrics.age_days,
            },
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Backend orchestration failed: ${response.statusText}`
          );
        }

        const data = await response.json();

        console.log('✅ Backend orchestration response:', data);

        const decision: AllocationDecision = {
          decision_id: data.decision_id,
          block_number: data.block_number,
          timestamp: data.timestamp,
          jediswap_pct: data.jediswap_pct,
          ekubo_pct: data.ekubo_pct,
          jediswap_risk: data.jediswap_risk,
          ekubo_risk: data.ekubo_risk,
          jediswap_apy: data.jediswap_apy,
          ekubo_apy: data.ekubo_apy,
          rationale_hash: data.rationale_hash,
          strategy_router_tx: data.strategy_router_tx,
          message: data.message,
        };

        return decision;
      } catch (err) {
        let errorMessage = 'Backend orchestration failed';
        if (err instanceof Error) {
          errorMessage = err.message;
        }
        console.error('❌ Backend orchestration error:', err);
        setError(errorMessage);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const getLatestDecision = useCallback(async (): Promise<AllocationDecision | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const config = getConfig();
      const backendUrl = config.backendUrl;

      if (!backendUrl) {
        throw new Error('Backend URL not configured');
      }

      console.log('📖 Fetching latest on-chain decision from backend...');

      // Call the same endpoint but with a GET to fetch latest decision
      // For MVP, we can use a simple POST with empty metrics to trigger a read
      const response = await fetch(`${backendUrl}/api/risk-engine/orchestrate-allocation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jediswap_metrics: {
            utilization: 0,
            volatility: 0,
            liquidity: 0,
            audit_score: 0,
            age_days: 0,
          },
          ekubo_metrics: {
            utilization: 0,
            volatility: 0,
            liquidity: 0,
            audit_score: 0,
            age_days: 0,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch decision: ${response.statusText}`);
      }

      const data = await response.json();

      const decision: AllocationDecision = {
        decision_id: data.decision_id,
        block_number: data.block_number,
        timestamp: data.timestamp,
        jediswap_pct: data.jediswap_pct,
        ekubo_pct: data.ekubo_pct,
        jediswap_risk: data.jediswap_risk,
        ekubo_risk: data.ekubo_risk,
        jediswap_apy: data.jediswap_apy,
        ekubo_apy: data.ekubo_apy,
        rationale_hash: data.rationale_hash,
        strategy_router_tx: data.strategy_router_tx,
        message: data.message,
      };

      return decision;
    } catch (err) {
      console.error('Error fetching decision:', err);
      setError('Failed to fetch decision');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    proposeAndExecuteAllocation,
    getLatestDecision,
    isLoading,
    error,
    clearError,
  };
}

