/**
 * ZKML Transparency Component
 * Displays proof/model information for transparency (5/5 zkML requirement)
 */
'use client';

import React from 'react';
import { HashLink } from './HashLink';
import { ProofStatusBadge } from './ProofStatusBadge';

interface ZkmlTransparencyProps {
  proofHash?: string;
  modelVersion?: string;
  modelHash?: string;
  verificationStatus?: 'verified' | 'pending' | 'failed';
  factRegistry?: string;
  proofSource?: 'luminair' | 'stone' | 'stone_prover';
  generationTime?: number;
  factHash?: string;
}

export const ZkmlTransparency: React.FC<ZkmlTransparencyProps> = ({
  proofHash,
  modelVersion = '1.0.0',
  modelHash,
  verificationStatus = 'pending',
  factRegistry = '0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c',
  proofSource = 'stone_prover',
  generationTime,
  factHash,
}) => {
  return (
    <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-white mb-1">zkML Transparency</h4>
        <p className="text-xs text-white/60">Proof and model provenance information</p>
      </div>

      <div className="space-y-3 text-sm">
        {proofHash && (
          <div>
            <p className="text-xs text-white/40 mb-1">Proof Hash</p>
            <HashLink hash={proofHash} type="search" />
          </div>
        )}

        {factHash && (
          <div>
            <p className="text-xs text-white/40 mb-1">Fact Hash</p>
            <HashLink hash={factHash} type="fact" />
          </div>
        )}

        {modelVersion && (
          <div>
            <p className="text-xs text-white/40 mb-1">Model Version</p>
            <p className="text-white/80">{modelVersion}</p>
          </div>
        )}

        {modelHash && (
          <div>
            <p className="text-xs text-white/40 mb-1">Model Hash</p>
            <HashLink hash={modelHash} type="search" />
          </div>
        )}

        <div>
          <p className="text-xs text-white/40 mb-1">Verification Status</p>
          <ProofStatusBadge 
            verified={verificationStatus === 'verified'} 
          />
        </div>

        {factRegistry && (
          <div>
            <p className="text-xs text-white/40 mb-1">Fact Registry</p>
            <HashLink hash={factRegistry} type="contract" />
          </div>
        )}

        {proofSource && (
          <div>
            <p className="text-xs text-white/40 mb-1">Proof Source</p>
            <p className="text-white/80 uppercase text-xs">{proofSource}</p>
          </div>
        )}

        {generationTime !== undefined && (
          <div>
            <p className="text-xs text-white/40 mb-1">Generation Time</p>
            <p className="text-white/80">{generationTime.toFixed(2)}s</p>
          </div>
        )}
      </div>
    </div>
  );
};
