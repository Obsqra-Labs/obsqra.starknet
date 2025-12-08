'use client';

import { useState, useCallback } from 'react';
import { getConfig } from '@/lib/config';

export interface RiskScoreProofRequest {
  utilization: number;
  volatility: number;
  liquidity: number;
  audit_score: number;
  age_days: number;
}

export interface AllocationProofRequest {
  nostra_risk: number;
  zklend_risk: number;
  ekubo_risk: number;
  nostra_apy: number;
  zklend_apy: number;
  ekubo_apy: number;
}

export interface ProofData {
  proof_hash: string;
  proof_id: string;
  computation_type: 'RISK_SCORE' | 'ALLOCATION';
  computation_trace: Record<string, any>;
  timestamp: string;
  verified: boolean;
}

export interface ProofResponse {
  proof: ProofData;
  verified: boolean;
  message: string;
}

export function useProofGeneration() {
  const [isGeneratingProof, setIsGeneratingProof] = useState(false);
  const [lastProof, setLastProof] = useState<ProofData | null>(null);
  const [proofError, setProofError] = useState<string | null>(null);

  const generateRiskScoreProof = useCallback(
    async (request: RiskScoreProofRequest): Promise<ProofData | null> => {
      setIsGeneratingProof(true);
      setProofError(null);

      try {
        const backendUrl = getConfig().backendUrl;
        const response = await fetch(`${backendUrl}/api/v1/proofs/risk-score`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          throw new Error(`Proof generation failed: ${response.statusText}`);
        }

        const data: ProofResponse = await response.json();
        setLastProof(data.proof);
        return data.proof;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to generate proof';
        setProofError(message);
        console.error('Risk proof generation error:', err);
        return null;
      } finally {
        setIsGeneratingProof(false);
      }
    },
    []
  );

  const generateAllocationProof = useCallback(
    async (request: AllocationProofRequest): Promise<ProofData | null> => {
      setIsGeneratingProof(true);
      setProofError(null);

      try {
        const backendUrl = getConfig().backendUrl;
        const response = await fetch(`${backendUrl}/api/v1/proofs/allocation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        });

        if (!response.ok) {
          throw new Error(`Proof generation failed: ${response.statusText}`);
        }

        const data: ProofResponse = await response.json();
        setLastProof(data.proof);
        return data.proof;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to generate proof';
        setProofError(message);
        console.error('Allocation proof generation error:', err);
        return null;
      } finally {
        setIsGeneratingProof(false);
      }
    },
    []
  );

  return {
    generateRiskScoreProof,
    generateAllocationProof,
    isGeneratingProof,
    lastProof,
    proofError,
  };
}

