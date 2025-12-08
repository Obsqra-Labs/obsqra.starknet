'use client';

interface DepositAllocationPreviewProps {
  depositAmount: number;
  jediswapPct: number;
  ekuboPct: number;
  latestDecisionId?: number;
  proofHash?: string;
}

export function DepositAllocationPreview({
  depositAmount,
  jediswapPct,
  ekuboPct,
  latestDecisionId,
  proofHash,
}: DepositAllocationPreviewProps) {
  const jediswapAmount = (depositAmount * jediswapPct) / 100;
  const ekuboAmount = (depositAmount * ekuboPct) / 100;

  return (
    <div className="bg-slate-800/50 border border-purple-500/20 rounded-lg p-4 mt-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">📊</span>
        <h3 className="text-sm font-semibold text-white">Allocation Preview</h3>
      </div>
      
      <p className="text-xs text-gray-400 mb-3">
        Your deposit will be allocated according to AI recommendation:
      </p>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded bg-blue-500"></div>
            <span className="text-xs font-medium text-blue-300">JediSwap</span>
          </div>
          <p className="text-lg font-bold text-white">{jediswapPct.toFixed(2)}%</p>
          <p className="text-xs text-gray-400">{jediswapAmount.toFixed(4)} STRK</p>
        </div>

        <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded bg-orange-500"></div>
            <span className="text-xs font-medium text-orange-300">Ekubo</span>
          </div>
          <p className="text-lg font-bold text-white">{ekuboPct.toFixed(2)}%</p>
          <p className="text-xs text-gray-400">{ekuboAmount.toFixed(4)} STRK</p>
        </div>
      </div>

      {(latestDecisionId || proofHash) && (
        <div className="pt-3 border-t border-white/10">
          <div className="flex items-center gap-2 text-xs">
            {latestDecisionId && (
              <span className="text-purple-300">
                ✅ Based on AI Decision #{latestDecisionId}
              </span>
            )}
            {proofHash && (
              <span className="text-gray-400">
                🔐 Proof: {proofHash.slice(0, 12)}...
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

