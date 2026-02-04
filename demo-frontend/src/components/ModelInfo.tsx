/**
 * Model Info Component
 * Displays current model version and provenance information
 */
import React from 'react';

interface ModelInfoProps {
  version: string;
  modelHash: string;
  deployedAt?: string;
  description?: string;
  isActive?: boolean;
}

export const ModelInfo: React.FC<ModelInfoProps> = ({
  version,
  modelHash,
  deployedAt,
  description = 'Risk scoring model for protocol allocation',
  isActive = true,
}) => {
  const formatHash = (hash: string) => {
    return `${hash.slice(0, 12)}...${hash.slice(-8)}`;
  };

  return (
    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-blue-900">Model Information</h4>
        {isActive && (
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded">
            Active
          </span>
        )}
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-blue-700 font-medium">Version:</span>
          <span className="text-blue-900 font-mono">{version}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-blue-700 font-medium">Model Hash:</span>
          <span className="text-blue-900 font-mono text-xs">{formatHash(modelHash)}</span>
        </div>
        
        {deployedAt && (
          <div className="flex justify-between">
            <span className="text-blue-700 font-medium">Deployed:</span>
            <span className="text-blue-900">{new Date(deployedAt).toLocaleDateString()}</span>
          </div>
        )}
        
        {description && (
          <div className="mt-2 pt-2 border-t border-blue-200">
            <p className="text-xs text-blue-600">{description}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModelInfo;
