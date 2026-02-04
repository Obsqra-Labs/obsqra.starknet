/**
 * Model Info Component
 * Displays current model version and provenance information
 */
'use client';

import React from 'react';
import { HashLink } from './HashLink';

interface ModelInfoProps {
  version: string;
  modelHash: string;
  deployedAt?: string;
  description?: string;
  isActive?: boolean;
  registryAddress?: string;
}

export const ModelInfo: React.FC<ModelInfoProps> = ({
  version,
  modelHash,
  deployedAt,
  description = 'Risk scoring model for protocol allocation',
  isActive = true,
  registryAddress,
}) => {
  return (
    <div className="bg-[#111113] border border-white/10 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-semibold text-white mb-1">Model Information</h4>
          <p className="text-xs text-white/60">On-chain model provenance</p>
        </div>
        {isActive && (
          <span className="px-2 py-1 text-xs bg-emerald-500/20 text-emerald-200 rounded-full border border-emerald-400/40">
            Active
          </span>
        )}
      </div>

      <div className="space-y-3 text-sm">
        <div>
          <p className="text-xs text-white/40 mb-1">Version</p>
          <p className="text-white/80 font-semibold">v{version}</p>
        </div>

        <div>
          <p className="text-xs text-white/40 mb-1">Model Hash</p>
          <HashLink hash={modelHash} type="search" />
        </div>

        {registryAddress && (
          <div>
            <p className="text-xs text-white/40 mb-1">Registry Address</p>
            <HashLink hash={registryAddress} type="contract" />
          </div>
        )}

        {deployedAt && (
          <div>
            <p className="text-xs text-white/40 mb-1">Deployed At</p>
            <p className="text-white/80">{new Date(deployedAt).toLocaleString()}</p>
          </div>
        )}

        {description && (
          <div className="pt-3 border-t border-white/10">
            <p className="text-xs text-white/40 mb-1">Description</p>
            <p className="text-white/80 text-xs">{description}</p>
          </div>
        )}
      </div>
    </div>
  );
};
