'use client';

import { useState, useCallback } from 'react';
import { getConfig } from '@/lib/config';

async function readErrorDetail(response: Response, fallback: string): Promise<string> {
  const rawText = await response.text().catch(() => '');
  if (!rawText) {
    return fallback;
  }
  try {
    const parsed = JSON.parse(rawText);
    
    // Handle new structured error format (Stone-only strict mode)
    if (parsed.detail) {
      // Check if detail is an object (structured error)
      if (typeof parsed.detail === 'object') {
        const errorObj = parsed.detail;
        const message = errorObj.message || errorObj.error || fallback;
        
        // Add strict mode indicator if present
        if (errorObj.strict_mode) {
          return `${message} (Strict Mode: No fallbacks available)`;
        }
        
        // Include fact_hash if available (for verification errors)
        if (errorObj.fact_hash) {
          return `${message}\nFact Hash: ${errorObj.fact_hash.slice(0, 20)}...`;
        }
        
        return message;
      }
      // If detail is a string, return it
      return parsed.detail;
    }
    
    return parsed.message || rawText;
  } catch {
    return rawText;
  }
}

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
  strategy_router_tx: string;  // Decision ID from contract (legacy)
  tx_hash?: string;  // Actual on-chain transaction hash
  message: string;
  proof_job_id?: string;
  proof_hash?: string;
  proof_status?: string;
  proof_error?: string;
}

/**
 * Allocation proposal (proof + preview, no execution)
 */
export interface AllocationProposal {
  proposal_id: string;
  block_number?: number;
  timestamp?: number;
  jediswap_pct: number;
  ekubo_pct: number;
  jediswap_risk: number;
  ekubo_risk: number;
  jediswap_apy: number;
  ekubo_apy: number;
  message: string;
  proof_job_id: string;
  proof_hash?: string;
  proof_status?: string;
  proof_error?: string;
  proof_source?: string;
  l2_verified_at?: string;
  can_execute?: boolean;
}

interface UseRiskEngineBackendOrchestrationReturn {
  proposeAllocation: (
    jediswapMetrics: ProtocolMetrics,
    ekuboMetrics: ProtocolMetrics
  ) => Promise<AllocationProposal | null>;
  proposeFromMarket: () => Promise<AllocationProposal | null>;
  executeAllocation: (proofJobId: string) => Promise<AllocationDecision | null>;
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

  const proposeAllocation = useCallback(
    async (
      jediswapMetrics: ProtocolMetrics,
      ekuboMetrics: ProtocolMetrics
    ): Promise<AllocationProposal | null> => {
      setIsLoading(true);
      setError(null);

      try {
        const config = getConfig();
        const backendUrl = config.backendUrl;

        console.log('🤖 Backend Proposal: Generating proof + allocation preview...');
        console.log('📊 JediSwap metrics:', jediswapMetrics);
        console.log('📊 Ekubo metrics:', ekuboMetrics);

        // Use relative path if no backend URL configured (Nginx will proxy to /api/...)
        // Otherwise use the configured backend URL
        const apiUrl = backendUrl 
          ? `${backendUrl}/api/v1/risk-engine/propose-allocation`
          : '/api/v1/risk-engine/propose-allocation';

        console.log('📍 API URL:', apiUrl);

        // Call backend proposal endpoint
        // The backend will:
        // 1. Generate proof + verify it
        // 2. Compute allocation preview (read-only)
        // 3. Return a proposal with proof status
        const response = await fetch(apiUrl, {
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
          const detail = await readErrorDetail(
            response,
            `Backend orchestration failed: ${response.status} ${response.statusText}`
          );
          throw new Error(detail);
        }

        const data = await response.json();

        console.log('✅ Backend proposal response:', data);

        const proposal: AllocationProposal = {
          proposal_id: data.proposal_id,
          block_number: data.block_number,
          timestamp: data.timestamp,
          jediswap_pct: data.jediswap_pct,
          ekubo_pct: data.ekubo_pct,
          jediswap_risk: data.jediswap_risk,
          ekubo_risk: data.ekubo_risk,
          jediswap_apy: data.jediswap_apy,
          ekubo_apy: data.ekubo_apy,
          message: data.message,
          proof_job_id: data.proof_job_id,
          proof_hash: data.proof_hash,
          proof_status: data.proof_status,
          proof_error: data.proof_error,
          proof_source: data.proof_source,
          l2_verified_at: data.l2_verified_at,
          can_execute: data.can_execute,
        };

        return proposal;
      } catch (err) {
        let errorMessage = 'Backend proposal failed';
        if (err instanceof Error) {
          errorMessage = err.message;
        }
        console.error('❌ Backend proposal error:', err);
        setError(errorMessage);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const proposeFromMarket = useCallback(async (): Promise<AllocationProposal | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const config = getConfig();
      const backendUrl = config.backendUrl;
      const apiUrl = backendUrl
        ? `${backendUrl}/api/v1/risk-engine/propose-from-market`
        : '/api/v1/risk-engine/propose-from-market';

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const detail = await readErrorDetail(
          response,
          `Market orchestration failed: ${response.status} ${response.statusText}`
        );
        throw new Error(detail);
      }

      const data = await response.json();

      const proposal: AllocationProposal = {
        proposal_id: data.proposal_id,
        block_number: data.block_number,
        timestamp: data.timestamp,
        jediswap_pct: data.jediswap_pct,
        ekubo_pct: data.ekubo_pct,
        jediswap_risk: data.jediswap_risk,
        ekubo_risk: data.ekubo_risk,
        jediswap_apy: data.jediswap_apy,
        ekubo_apy: data.ekubo_apy,
        message: data.message,
        proof_job_id: data.proof_job_id,
        proof_hash: data.proof_hash,
        proof_status: data.proof_status,
        proof_error: data.proof_error,
        proof_source: data.proof_source,
        l2_verified_at: data.l2_verified_at,
        can_execute: data.can_execute,
      };

      return proposal;
    } catch (err) {
      let errorMessage = 'Market proposal failed';
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      console.error('❌ Market proposal error:', err);
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const executeAllocation = useCallback(async (proofJobId: string): Promise<AllocationDecision | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const config = getConfig();
      const backendUrl = config.backendUrl;
      const apiUrl = backendUrl
        ? `${backendUrl}/api/v1/risk-engine/execute-allocation`
        : '/api/v1/risk-engine/execute-allocation';

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ proof_job_id: proofJobId }),
      });

      if (!response.ok) {
        const detail = await readErrorDetail(
          response,
          `Execution failed: ${response.status} ${response.statusText}`
        );
        throw new Error(detail);
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
        tx_hash: data.tx_hash,
        message: data.message,
        proof_job_id: data.proof_job_id,
        proof_hash: data.proof_hash,
        proof_status: data.proof_status,
        proof_error: data.proof_error,
      };

      return decision;
    } catch (err) {
      let errorMessage = 'Execution failed';
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      console.error('❌ Execution error:', err);
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

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
      const response = await fetch(`${backendUrl}/api/v1/risk-engine/orchestrate-allocation`, {
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
        tx_hash: data.tx_hash,
        message: data.message,
        proof_job_id: data.proof_job_id,
        proof_hash: data.proof_hash,
        proof_status: data.proof_status,
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
    proposeAllocation,
    proposeFromMarket,
    executeAllocation,
    getLatestDecision,
    isLoading,
    error,
    clearError,
  };
}
