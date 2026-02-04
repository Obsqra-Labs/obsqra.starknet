'use client';

import { getContractUrl, getTransactionUrl, getSearchUrl, getFactRegistryQueryUrl } from '@/lib/blockExplorer';
import { getConfig } from '@/lib/config';

interface HashLinkProps {
  hash: string;
  type?: 'contract' | 'transaction' | 'fact' | 'search';
  label?: string;
  className?: string;
  showIcon?: boolean;
  truncate?: boolean;
}

export function HashLink({ 
  hash, 
  type = 'search', 
  label,
  className = '',
  showIcon = true,
  truncate = true 
}: HashLinkProps) {
  const config = getConfig();
  const network = config.networkName;

  if (!hash || !hash.startsWith('0x')) {
    return <span className={className}>—</span>;
  }

  let url = '';
  switch (type) {
    case 'contract':
      url = getContractUrl(hash, network);
      break;
    case 'transaction':
      url = getTransactionUrl(hash, network);
      break;
    case 'fact':
      url = getFactRegistryQueryUrl(hash, network);
      break;
    case 'search':
    default:
      url = getSearchUrl(hash, network);
      break;
  }

  if (!url) {
    return <span className={`font-mono ${className}`}>{hash}</span>;
  }

  const displayHash = truncate && hash.length > 16 
    ? `${hash.slice(0, 10)}…${hash.slice(-8)}`
    : hash;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center gap-1.5 font-mono text-blue-400 hover:text-blue-300 transition-colors ${className}`}
      title={hash}
    >
      {label || displayHash}
      {showIcon && (
        <svg className="w-3 h-3 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
      )}
    </a>
  );
}
