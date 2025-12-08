'use client';

import { useMemo } from 'react';

interface ProtocolStats {
  name: string;
  icon: string;
  allocation: number;
  apy: number;
  tvl: string;
  risk: 'low' | 'medium' | 'high';
  change24h: number;
  color: string;
}

interface AnalyticsDashboardProps {
  allocation: { jediswap: number; ekubo: number } | null;
  isDemoMode?: boolean;
}

export function AnalyticsDashboard({ allocation, isDemoMode = false }: AnalyticsDashboardProps) {
  const protocolStats: ProtocolStats[] = useMemo(() => {
    const jediAlloc = allocation?.jediswap ?? 50;
    const ekuboAlloc = allocation?.ekubo ?? 50;

    return [
      {
        name: 'JediSwap',
        icon: '🔄',
        allocation: jediAlloc,
        apy: isDemoMode ? 8.5 : 5.2,
        tvl: isDemoMode ? '$2.5M' : '$1.8M',
        risk: 'low',
        change24h: isDemoMode ? 2.3 : 1.1,
        color: 'blue',
      },
      {
        name: 'Ekubo',
        icon: '🌀',
        allocation: ekuboAlloc,
        apy: isDemoMode ? 12.8 : 8.5,
        tvl: isDemoMode ? '$3.2M' : '$2.1M',
        risk: 'medium',
        change24h: isDemoMode ? 5.7 : 2.4,
        color: 'orange',
      },
    ];
  }, [allocation, isDemoMode]);

  const totalAPY = useMemo(() => {
    return protocolStats.reduce((sum, protocol) => {
      return sum + (protocol.apy * protocol.allocation / 100);
    }, 0);
  }, [protocolStats]);

  const portfolioValue = isDemoMode ? 1000 : 100;

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue': return {
        bg: 'from-blue-600/20 to-blue-500/10',
        border: 'border-blue-500/30',
        text: 'text-blue-400',
        bar: 'from-blue-500 to-blue-600',
      };
      case 'orange': return {
        bg: 'from-orange-600/20 to-orange-500/10',
        border: 'border-orange-500/30',
        text: 'text-orange-400',
        bar: 'from-orange-500 to-orange-600',
      };
      default: return {
        bg: 'from-purple-600/20 to-purple-500/10',
        border: 'border-purple-500/30',
        text: 'text-purple-400',
        bar: 'from-purple-500 to-purple-600',
      };
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Indicator */}
      <div className={`px-4 py-2 rounded-xl border text-sm font-semibold flex items-center gap-2 ${
        isDemoMode 
          ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400' 
          : 'bg-green-500/10 border-green-500/30 text-green-400'
      }`}>
        {isDemoMode ? '🎮 Demo Mode - Simulated Data' : '✅ Live Mode - StrategyRouterV2'}
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-600/20 to-purple-500/10 border border-purple-500/30 rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Portfolio Value</p>
          <p className="text-2xl font-bold text-white">{portfolioValue.toFixed(2)} STRK</p>
        </div>

        <div className="bg-gradient-to-br from-blue-600/20 to-cyan-600/10 border border-blue-500/30 rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Weighted APY</p>
          <p className="text-2xl font-bold text-green-400">{totalAPY.toFixed(2)}%</p>
        </div>

        <div className="bg-gradient-to-br from-green-600/20 to-emerald-600/10 border border-green-500/30 rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Est. Daily Yield</p>
          <p className="text-2xl font-bold text-white">
            {((portfolioValue * totalAPY / 100) / 365).toFixed(4)} STRK
          </p>
        </div>

        <div className="bg-gradient-to-br from-orange-600/20 to-red-600/10 border border-orange-500/30 rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Risk Score</p>
          <p className="text-2xl font-bold text-yellow-400">45/100</p>
          <p className="text-xs text-gray-500">Moderate</p>
        </div>
      </div>

      {/* Protocol Cards */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-white">Protocol Performance</h3>
        
        {protocolStats.map((protocol) => {
          const colors = getColorClasses(protocol.color);
          return (
            <div
              key={protocol.name}
              className={`bg-gradient-to-br ${colors.bg} border ${colors.border} rounded-xl p-5 transition-all hover:scale-[1.01]`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{protocol.icon}</span>
                  <div>
                    <h4 className="text-lg font-bold text-white">{protocol.name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${getRiskBadge(protocol.risk)}`}>
                        {protocol.risk} risk
                      </span>
                      <span className="text-xs text-gray-400">TVL: {protocol.tvl}</span>
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <p className="text-3xl font-bold text-white">{protocol.allocation.toFixed(1)}%</p>
                  <p className="text-sm text-gray-400">allocated</p>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-700/50 rounded-full h-2 mb-4">
                <div
                  className={`bg-gradient-to-r ${colors.bar} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${protocol.allocation}%` }}
                />
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">APY</span>
                  <p className="text-green-400 font-bold">{protocol.apy}%</p>
                </div>
                <div>
                  <span className="text-gray-400">24h Change</span>
                  <p className={protocol.change24h >= 0 ? 'text-green-400 font-bold' : 'text-red-400 font-bold'}>
                    {protocol.change24h >= 0 ? '+' : ''}{protocol.change24h.toFixed(2)}%
                  </p>
                </div>
                <div>
                  <span className="text-gray-400">Est. Yield/Year</span>
                  <p className="text-white font-bold">
                    {((portfolioValue * protocol.allocation / 100) * (protocol.apy / 100)).toFixed(2)} STRK
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Risk Analysis */}
      <div className="bg-black/30 border border-purple-500/20 rounded-xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">Risk Analysis</h3>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-400">Diversification</span>
              <span className="text-green-400 font-medium">Good</span>
            </div>
            <div className="w-full bg-gray-700/50 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '75%' }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Split across 2 protocols for balanced exposure
            </p>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-400">Protocol Risk</span>
              <span className="text-yellow-400 font-medium">Moderate</span>
            </div>
            <div className="w-full bg-gray-700/50 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '45%' }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Both protocols are audited and battle-tested on Starknet
            </p>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-400">Liquidity Risk</span>
              <span className="text-green-400 font-medium">Low</span>
            </div>
            <div className="w-full bg-gray-700/50 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '20%' }} />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Sufficient liquidity for position sizes
            </p>
          </div>
        </div>
      </div>

      {/* Projected Returns */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-black/30 border border-purple-500/20 rounded-xl p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">7-Day Projection</p>
          <p className="text-2xl font-bold text-green-400">
            +{((portfolioValue * totalAPY / 100) / 52).toFixed(4)} STRK
          </p>
        </div>
        <div className="bg-black/30 border border-purple-500/20 rounded-xl p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">30-Day Projection</p>
          <p className="text-2xl font-bold text-green-400">
            +{((portfolioValue * totalAPY / 100) / 12).toFixed(4)} STRK
          </p>
        </div>
        <div className="bg-black/30 border border-purple-500/20 rounded-xl p-4 text-center">
          <p className="text-sm text-gray-400 mb-1">Annual Projection</p>
          <p className="text-2xl font-bold text-purple-400">
            +{(portfolioValue * totalAPY / 100).toFixed(2)} STRK
          </p>
        </div>
      </div>
    </div>
  );
}
