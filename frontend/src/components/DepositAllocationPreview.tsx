'use client';

interface DepositAllocationPreviewProps {
  depositAmount: number;
  jediswapPct: number;
  ekuboPct: number;
  latestDecisionId?: number;
  proofHash?: string;
  latestRecommendation?: {
    jediswap_pct: number;
    ekubo_pct: number;
  } | null;
}

export function DepositAllocationPreview({
  depositAmount,
  jediswapPct,
  ekuboPct,
  latestDecisionId,
  proofHash,
  latestRecommendation,
}: DepositAllocationPreviewProps) {
  const jediswapAmount = (depositAmount * jediswapPct) / 100;
  const ekuboAmount = (depositAmount * ekuboPct) / 100;
  
  // Check if current allocation matches latest AI recommendation
  const allocationMatches = latestRecommendation ? (
    Math.abs(jediswapPct - latestRecommendation.jediswap_pct) < 0.1 &&
    Math.abs(ekuboPct - latestRecommendation.ekubo_pct) < 0.1
  ) : null;

  return (
    <div className="bg-slate-800/50 border border-purple-500/20 rounded-lg p-4 mt-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">📊</span>
        <h3 className="text-sm font-semibold text-white">Allocation Preview</h3>
      </div>
      
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs text-gray-400">
          Your deposit will be allocated according to AI recommendation:
        </p>
        {allocationMatches === true && (
          <span className="text-xs px-2 py-1 bg-green-500/20 text-green-400 border border-green-500/30 rounded">
            ✅ Matches AI
          </span>
        )}
        {allocationMatches === false && (
          <span className="text-xs px-2 py-1 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 rounded">
            ⚠️ Different from latest
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded bg-blue-500"></div>
            <span className="text-xs font-medium text-blue-300">JediSwap</span>
          </div>
          <p className="text-lg font-bold text-white">{jediswapPct.toFixed(2)}%</p>
          <p className="text-xs text-gray-400">{jediswapAmount.toFixed(4)} ETH</p>
        </div>

        <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded bg-orange-500"></div>
            <span className="text-xs font-medium text-orange-300">Ekubo</span>
          </div>
          <p className="text-lg font-bold text-white">{ekuboPct.toFixed(2)}%</p>
          <p className="text-xs text-gray-400">{ekuboAmount.toFixed(4)} ETH</p>
        </div>
      </div>

      {(latestDecisionId || proofHash || allocationMatches === false) && (
        <div className="pt-3 border-t border-white/10">
          <div className="space-y-1 text-xs">
            {latestDecisionId && (
              <div className="flex items-center gap-2">
                <span className="text-purple-300">
                  ✅ Based on AI Decision #{latestDecisionId}
                </span>
              </div>
            )}
            {proofHash && allocationMatches === true && (
              <div className="flex items-center gap-2">
                <span className="text-green-400">
                  🔐 Verified Proof: {proofHash.slice(0, 12)}...
                </span>
              </div>
            )}
            {allocationMatches === false && latestRecommendation && (
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded p-2">
                <p className="text-yellow-400 text-xs mb-1">
                  ⚠️ Current allocation differs from latest AI recommendation:
                </p>
                <div className="text-xs text-gray-300 space-y-0.5">
                  <div>Current: JediSwap {jediswapPct.toFixed(2)}%, Ekubo {ekuboPct.toFixed(2)}%</div>
                  <div>Latest AI: JediSwap {latestRecommendation.jediswap_pct.toFixed(2)}%, Ekubo {latestRecommendation.ekubo_pct.toFixed(2)}%</div>
                </div>
                <p className="text-yellow-300/70 text-xs mt-1">
                  Consider running AI orchestration to update allocation
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

