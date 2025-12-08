'use client';

import { useAccount } from '@starknet-react/core';
import { Contract, AccountInterface, Abi } from 'starknet';
import { useState, useCallback } from 'react';
import { getConfig } from '@/lib/config';

/**
 * Protocol metrics for RiskEngine orchestration
 */
export interface ProtocolMetrics {
  utilization: number; // 0-10000 basis points
  volatility: number;   // 0-10000 basis points
  liquidity: number;    // 0-3 categorical
  auditScore: number;   // 0-100
  ageDays: number;      // days
}

/**
 * Allocation decision from RiskEngine
 */
export interface AllocationDecision {
  decisionId: number;
  blockNumber: number;
  timestamp: number;
  jediswapPct: number;
  ekuboPct: number;
  jediswapRisk: number;
  ekuboRisk: number;
  jediswapApy: number;
  ekuboApy: number;
  rationaleHash: string;
  strategyRouterTx: string;
}

const RISK_ENGINE_ABI = [
  {
    type: 'function',
    name: 'propose_and_execute_allocation',
    inputs: [
      {
        name: 'jediswap_metrics',
        type: 'struct',
        members: [
          { name: 'utilization', type: 'felt252' },
          { name: 'volatility', type: 'felt252' },
          { name: 'liquidity', type: 'felt252' },
          { name: 'audit_score', type: 'felt252' },
          { name: 'age_days', type: 'felt252' },
        ],
      },
      {
        name: 'ekubo_metrics',
        type: 'struct',
        members: [
          { name: 'utilization', type: 'felt252' },
          { name: 'volatility', type: 'felt252' },
          { name: 'liquidity', type: 'felt252' },
          { name: 'audit_score', type: 'felt252' },
          { name: 'age_days', type: 'felt252' },
        ],
      },
    ],
    outputs: [
      {
        name: 'decision',
        type: 'struct',
        members: [
          { name: 'decision_id', type: 'felt252' },
          { name: 'block_number', type: 'u64' },
          { name: 'timestamp', type: 'u64' },
          { name: 'jediswap_pct', type: 'felt252' },
          { name: 'ekubo_pct', type: 'felt252' },
          { name: 'jediswap_risk', type: 'felt252' },
          { name: 'ekubo_risk', type: 'felt252' },
          { name: 'jediswap_apy', type: 'felt252' },
          { name: 'ekubo_apy', type: 'felt252' },
          { name: 'rationale_hash', type: 'felt252' },
          { name: 'strategy_router_tx', type: 'felt252' },
        ],
      },
    ],
    stateMutability: 'external',
  },
  {
    type: 'function',
    name: 'get_decision',
    inputs: [{ name: 'decision_id', type: 'felt252' }],
    outputs: [
      {
        name: 'decision',
        type: 'struct',
        members: [
          { name: 'decision_id', type: 'felt252' },
          { name: 'block_number', type: 'u64' },
          { name: 'timestamp', type: 'u64' },
          { name: 'jediswap_pct', type: 'felt252' },
          { name: 'ekubo_pct', type: 'felt252' },
          { name: 'jediswap_risk', type: 'felt252' },
          { name: 'ekubo_risk', type: 'felt252' },
          { name: 'jediswap_apy', type: 'felt252' },
          { name: 'ekubo_apy', type: 'felt252' },
          { name: 'rationale_hash', type: 'felt252' },
          { name: 'strategy_router_tx', type: 'felt252' },
        ],
      },
    ],
    stateMutability: 'view',
  },
  {
    type: 'function',
    name: 'get_decision_count',
    inputs: [],
    outputs: [{ name: 'count', type: 'felt252' }],
    stateMutability: 'view',
  },
] as Abi;

export interface UseRiskEngineOrchestrationReturn {
  proposeAndExecuteAllocation: (
    jediswapMetrics: ProtocolMetrics,
    ekuboMetrics: ProtocolMetrics
  ) => Promise<AllocationDecision | null>;
  getDecision: (decisionId: number) => Promise<AllocationDecision | null>;
  getDecisionCount: () => Promise<number | null>;
  isLoading: boolean;
  error: string | null;
  lastDecision: AllocationDecision | null;
  clearError: () => void;
}

export function useRiskEngineOrchestration(): UseRiskEngineOrchestrationReturn {
  const { account, address } = useAccount();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastDecision, setLastDecision] = useState<AllocationDecision | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const proposeAndExecuteAllocation = useCallback(
    async (
      jediswapMetrics: ProtocolMetrics,
      ekuboMetrics: ProtocolMetrics
    ): Promise<AllocationDecision | null> => {
      if (!account || !address) {
        setError('Wallet not connected');
        return null;
      }

      setIsLoading(true);
      setError(null);

      try {
        const config = getConfig();
        const riskEngineAddress = config.riskEngineAddress;

        if (!riskEngineAddress) {
          throw new Error('Risk Engine address not configured');
        }

        // Create contract instance
        const contract = new Contract(
          RISK_ENGINE_ABI,
          riskEngineAddress,
          account as unknown as AccountInterface
        );

        // Prepare metrics structs - Starknet.js expects structs as objects with field names matching ABI
        const jediswapMetricsStruct = {
          utilization: jediswapMetrics.utilization,
          volatility: jediswapMetrics.volatility,
          liquidity: jediswapMetrics.liquidity,
          audit_score: jediswapMetrics.auditScore,  // ABI uses snake_case
          age_days: jediswapMetrics.ageDays,        // ABI uses snake_case
        };

        const ekuboMetricsStruct = {
          utilization: ekuboMetrics.utilization,
          volatility: ekuboMetrics.volatility,
          liquidity: ekuboMetrics.liquidity,
          audit_score: ekuboMetrics.auditScore,      // ABI uses snake_case
          age_days: ekuboMetrics.ageDays,            // ABI uses snake_case
        };

        console.log('🤖 RiskEngine Orchestration: Proposing and executing allocation...');
        console.log('📊 JediSwap metrics struct:', jediswapMetricsStruct);
        console.log('📊 Ekubo metrics struct:', ekuboMetricsStruct);

        // Call propose_and_execute_allocation
        const response = await contract.invoke('propose_and_execute_allocation', [
          jediswapMetricsStruct,
          ekuboMetricsStruct,
        ]);

        const txHash = response.transaction_hash;
        console.log('✅ RiskEngine orchestration transaction sent:', txHash);

        // Wait for transaction to be confirmed
        // Note: In production, you'd want to wait for receipt
        // For now, we'll fetch the decision after a short delay
        await new Promise((resolve) => setTimeout(resolve, 5000));

        // Fetch the decision (using latest decision_id)
        const decisionCount = await contract.call('get_decision_count', []);
        const latestDecisionId = Number(
          (decisionCount as any)?.[0] ??
            (decisionCount as any)?.decision_count ??
            0,
        );

        if (latestDecisionId > 0) {
          const decisionResult = await contract.call('get_decision', [latestDecisionId]);
          const decisionData =
            (decisionResult as any)?.[0] ??
            (decisionResult as any)?.decision ??
            (decisionResult as any) ??
            {};

          const decision: AllocationDecision = {
            decisionId: Number(decisionData.decision_id),
            blockNumber: Number(decisionData.block_number),
            timestamp: Number(decisionData.timestamp),
            jediswapPct: Number(decisionData.jediswap_pct) / 100, // Convert from basis points
            ekuboPct: Number(decisionData.ekubo_pct) / 100,
            jediswapRisk: Number(decisionData.jediswap_risk),
            ekuboRisk: Number(decisionData.ekubo_risk),
            jediswapApy: Number(decisionData.jediswap_apy) / 100,
            ekuboApy: Number(decisionData.ekubo_apy) / 100,
            rationaleHash: decisionData.rationale_hash.toString(),
            strategyRouterTx: decisionData.strategy_router_tx.toString(),
          };

          setLastDecision(decision);
          console.log('✅ Allocation decision received:', decision);
          return decision;
        }

        return null;
      } catch (err) {
        let errorMessage = 'RiskEngine orchestration failed';
        if (err instanceof Error) {
          errorMessage = err.message;
        }
        console.error('❌ RiskEngine orchestration error:', err);
        setError(errorMessage);
        return null;
      } finally {
        setIsLoading(false);
      }
    },
    [account, address]
  );

  const getDecision = useCallback(
    async (decisionId: number): Promise<AllocationDecision | null> => {
      if (!account || !address) {
        setError('Wallet not connected');
        return null;
      }

      try {
        const config = getConfig();
        const riskEngineAddress = config.riskEngineAddress;

        if (!riskEngineAddress) {
          throw new Error('Risk Engine address not configured');
        }

        const contract = new Contract(
          RISK_ENGINE_ABI,
          riskEngineAddress,
          account as unknown as AccountInterface
        );

        const decisionResult = await contract.call('get_decision', [decisionId]);
        const decisionData =
          (decisionResult as any)?.[0] ??
          (decisionResult as any)?.decision ??
          (decisionResult as any) ??
          {};

        const decision: AllocationDecision = {
          decisionId: Number(decisionData.decision_id),
          blockNumber: Number(decisionData.block_number),
          timestamp: Number(decisionData.timestamp),
          jediswapPct: Number(decisionData.jediswap_pct) / 100,
          ekuboPct: Number(decisionData.ekubo_pct) / 100,
          jediswapRisk: Number(decisionData.jediswap_risk),
          ekuboRisk: Number(decisionData.ekubo_risk),
          jediswapApy: Number(decisionData.jediswap_apy) / 100,
          ekuboApy: Number(decisionData.ekubo_apy) / 100,
          rationaleHash: decisionData.rationale_hash.toString(),
          strategyRouterTx: decisionData.strategy_router_tx.toString(),
        };

        return decision;
      } catch (err) {
        console.error('❌ Error fetching decision:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch decision');
        return null;
      }
    },
    [account, address]
  );

  const getDecisionCount = useCallback(async (): Promise<number | null> => {
    if (!account || !address) {
      return null;
    }

    try {
      const config = getConfig();
      const riskEngineAddress = config.riskEngineAddress;

      if (!riskEngineAddress) {
        return null;
      }

      const contract = new Contract(
        RISK_ENGINE_ABI,
        riskEngineAddress,
        account as unknown as AccountInterface
      );

      const result = await contract.call('get_decision_count', []);
      return Number(
        (result as any)?.[0] ??
          (result as any)?.decision_count ??
          0,
      );
    } catch (err) {
      console.error('❌ Error fetching decision count:', err);
      return null;
    }
  }, [account, address]);

  return {
    proposeAndExecuteAllocation,
    getDecision,
    getDecisionCount,
    isLoading,
    error,
    lastDecision,
    clearError,
  };
}
