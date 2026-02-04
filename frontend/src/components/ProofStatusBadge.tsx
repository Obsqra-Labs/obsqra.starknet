'use client';

interface ProofStatusBadgeProps {
  verified: boolean;
  verifiedAt?: string;
  className?: string;
}

export function ProofStatusBadge({ verified, verifiedAt, className = '' }: ProofStatusBadgeProps) {
  if (verified) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-200 text-xs font-medium ${className}`}>
        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
        <span>Verified</span>
        {verifiedAt && (
          <span className="text-emerald-300/70 text-[10px]">
            {new Date(verifiedAt).toLocaleTimeString()}
          </span>
        )}
      </div>
    );
  }

  return (
      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-yellow-500/20 border border-yellow-400/40 text-yellow-200 text-xs font-medium ${className}`}>
        <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
        </svg>
        <span>Pending</span>
    </div>
  );
}
