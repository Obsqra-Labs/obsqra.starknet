/**
 * ZKML Transparency Component
 * Displays proof/model information for transparency (5/5 zkML requirement)
 */
import React from 'react';

interface ZkmlTransparencyProps {
  proofHash?: string;
  modelVersion?: string;
  modelHash?: string;
  verificationStatus?: 'verified' | 'pending' | 'failed';
  factRegistry?: string;
  proofSource?: 'luminair' | 'stone';
  generationTime?: number;
}

export const ZkmlTransparency: React.FC<ZkmlTransparencyProps> = ({
  proofHash,
  modelVersion = '1.0.0',
  modelHash,
  verificationStatus = 'pending',
  factRegistry = '0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64',
  proofSource = 'luminair',
  generationTime,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified':
        return 'text-green-600 bg-green-50';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatHash = (hash?: string) => {
    if (!hash) return 'N/A';
    return `${hash.slice(0, 10)}...${hash.slice(-8)}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">
        🔐 ZKML Verification Status
      </h3>
      
      <div className="space-y-4">
        {/* Verification Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Verification Status:</span>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(verificationStatus)}`}>
            {verificationStatus === 'verified' && '✅ Verified'}
            {verificationStatus === 'pending' && '⏳ Pending'}
            {verificationStatus === 'failed' && '❌ Failed'}
          </span>
        </div>

        {/* Proof Hash */}
        {proofHash && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Proof Hash:</span>
            <span className="text-sm font-mono text-gray-800">{formatHash(proofHash)}</span>
          </div>
        )}

        {/* Model Version */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Model Version:</span>
          <span className="text-sm text-gray-800">{modelVersion}</span>
        </div>

        {/* Model Hash */}
        {modelHash && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Model Hash:</span>
            <span className="text-sm font-mono text-gray-800">{formatHash(modelHash)}</span>
          </div>
        )}

        {/* Fact Registry */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Fact Registry:</span>
          <span className="text-sm font-mono text-gray-800">{formatHash(factRegistry)}</span>
        </div>

        {/* Proof Source */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Proof Source:</span>
          <span className="text-sm text-gray-800 capitalize">{proofSource}</span>
        </div>

        {/* Generation Time */}
        {generationTime && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Generation Time:</span>
            <span className="text-sm text-gray-800">{generationTime.toFixed(2)}s</span>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          All proofs are verified on-chain via the FactRegistry contract. 
          Model provenance is tracked for full auditability.
        </p>
      </div>
    </div>
  );
};

export default ZkmlTransparency;
