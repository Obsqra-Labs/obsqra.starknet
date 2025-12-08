'use client';

import { useState } from 'react';

export type ProofStatus = 'generated' | 'submitted' | 'verifying' | 'verified' | 'failed';

interface ProofBadgeProps {
  hash: string;
  status: ProofStatus;
  txHash?: string | null;
  factHash?: string | null;
  submittedAt?: string | null;
  verifiedAt?: string | null;
}

export function ProofBadge({ hash, status, txHash, factHash, submittedAt, verifiedAt, proofJobId }: ProofBadgeProps) {
  const [showDetails, setShowDetails] = useState(false);

  const statusConfig = {
    generated: {
      icon: '⏳',
      color: 'yellow',
      bg: 'bg-yellow-500/20',
      border: 'border-yellow-500/30',
      text: 'text-yellow-400',
      label: 'Generated',
    },
    submitted: {
      icon: '✓',
      color: 'blue',
      bg: 'bg-blue-500/20',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      label: 'Submitted',
    },
    verifying: {
      icon: '🔄',
      color: 'orange',
      bg: 'bg-orange-500/20',
      border: 'border-orange-500/30',
      text: 'text-orange-400',
      label: 'Verifying',
    },
    verified: {
      icon: '✅',
      color: 'green',
      bg: 'bg-green-500/20',
      border: 'border-green-500/30',
      text: 'text-green-400',
      label: 'Verified',
    },
    failed: {
      icon: '❌',
      color: 'red',
      bg: 'bg-red-500/20',
      border: 'border-red-500/30',
      text: 'text-red-400',
      label: 'Failed',
    },
  };

  const config = statusConfig[status] || statusConfig.generated;
  const truncatedHash = `${hash.slice(0, 10)}...${hash.slice(-6)}`;

  return (
    <div className="relative inline-block">
      <div
        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${config.bg} ${config.border} cursor-pointer hover:scale-105 transition-transform`}
        onMouseEnter={() => setShowDetails(true)}
        onMouseLeave={() => setShowDetails(false)}
      >
        <span className="text-sm">{config.icon}</span>
        <code className={`text-xs font-mono ${config.text}`}>{truncatedHash}</code>
        <span className={`text-xs font-medium ${config.text}`}>{config.label}</span>
      </div>

      {/* Tooltip with full details */}
      {showDetails && (
        <div className="absolute z-50 bottom-full left-0 mb-2 w-80 p-4 bg-slate-900 border border-white/20 rounded-lg shadow-xl">
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-lg">{config.icon}</span>
              <h3 className={`font-bold ${config.text}`}>STARK Proof {config.label}</h3>
            </div>
            
            <div>
              <p className="text-xs text-gray-400 mb-1">Proof Hash:</p>
              <code className="text-xs text-white break-all">{hash}</code>
            </div>

            {txHash && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Transaction:</p>
                <a
                  href={`https://sepolia.voyager.online/tx/${txHash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-400 hover:text-blue-300 break-all"
                >
                  {txHash}
                </a>
              </div>
            )}

            {factHash && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Fact Hash (L1):</p>
                <code className="text-xs text-green-400 break-all">{factHash}</code>
              </div>
            )}

            {verifiedAt && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Verified:</p>
                <p className="text-xs text-green-400 font-semibold">{new Date(verifiedAt).toLocaleString()}</p>
              </div>
            )}

            {submittedAt && (
              <div>
                <p className="text-xs text-gray-400 mb-1">On-Chain:</p>
                <p className="text-xs text-white">{new Date(submittedAt).toLocaleString()}</p>
              </div>
            )}

            {proofJobId && (
              <div className="mt-2">
                <a
                  href={`/api/v1/analytics/proof/${proofJobId}/download`}
                  download
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 rounded text-xs text-blue-300 transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  📥 Download Proof
                </a>
              </div>
            )}

            <div className="mt-3 pt-3 border-t border-white/10">
              <p className="text-xs text-gray-400">
                {status === 'verified' && (
                  <>
                    ✅ <span className="text-green-400 font-semibold">Locally verified</span> (<1 second)
                    <br />
                    <span className="text-gray-500 text-[10px] mt-1 block">Cryptographic proof of computation integrity</span>
                  </>
                )}
                {status === 'verifying' && '⏳ SHARP verification in progress (10-60 min)'}
                {status === 'submitted' && (
                  <>
                    📡 On-chain execution succeeded
                    <br />
                    <span className="text-gray-500 text-[10px] mt-1 block">Proof verified locally before execution</span>
                  </>
                )}
                {status === 'generated' && '🔐 Cryptographic proof generated (verification pending)'}
                {status === 'failed' && '❌ Verification or execution failed'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

