'use client';

interface AllocationDisplayProps {
  jediswapPct: number;
  ekuboPct: number;
  jediswapRisk?: number;
  ekuboRisk?: number;
  className?: string;
}

export function AllocationDisplay({ 
  jediswapPct, 
  ekuboPct, 
  jediswapRisk,
  ekuboRisk,
  className = '' 
}: AllocationDisplayProps) {
  const jediswapPercent = jediswapPct / 100;
  const ekuboPercent = ekuboPct / 100;
  const total = jediswapPercent + ekuboPercent;

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Visual Bar */}
      <div className="w-full h-8 bg-white/5 rounded-lg overflow-hidden flex">
        <div
          className="bg-emerald-500/40 flex items-center justify-center text-xs font-semibold text-white transition-all"
          style={{ width: `${(jediswapPercent / total) * 100}%` }}
        >
          {jediswapPercent.toFixed(1)}%
        </div>
        <div
          className="bg-cyan-500/40 flex items-center justify-center text-xs font-semibold text-white transition-all"
          style={{ width: `${(ekuboPercent / total) * 100}%` }}
        >
          {ekuboPercent.toFixed(1)}%
        </div>
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-emerald-500/40" />
            <span className="font-semibold">JediSwap</span>
          </div>
          <div className="pl-5 text-white/70">
            <div>{jediswapPercent.toFixed(2)}% allocation</div>
            {jediswapRisk !== undefined && (
              <div className="text-xs text-white/50">Risk: {jediswapRisk}</div>
            )}
          </div>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded bg-cyan-500/40" />
            <span className="font-semibold">Ekubo</span>
          </div>
          <div className="pl-5 text-white/70">
            <div>{ekuboPercent.toFixed(2)}% allocation</div>
            {ekuboRisk !== undefined && (
              <div className="text-xs text-white/50">Risk: {ekuboRisk}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
