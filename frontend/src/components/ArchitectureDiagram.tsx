'use client';

interface ArchitectureDiagramProps {
  variant?: 'stack' | 'comparison' | 'flow';
  className?: string;
}

export function ArchitectureDiagram({ variant = 'stack', className = '' }: ArchitectureDiagramProps) {
  if (variant === 'comparison') {
    return <ComparisonDiagram className={className} />;
  }
  
  if (variant === 'flow') {
    return <FlowDiagram className={className} />;
  }
  
  return <StackDiagram className={className} />;
}

function StackDiagram({ className }: { className: string }) {
  return (
    <div className={`bg-slate-900 text-white rounded-2xl p-6 ${className}`}>
      <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">
        Starknet Obsqra Stack
      </h3>
      
      <div className="space-y-3">
        {/* User Layer */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-mint-500 to-lagoon-500 flex items-center justify-center text-lg">
              👤
            </div>
            <div>
              <p className="font-semibold text-white">User Layer</p>
              <p className="text-sm text-slate-400">Wallet connection (Argent X, Braavos)</p>
            </div>
          </div>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <div className="w-0.5 h-6 bg-gradient-to-b from-mint-500 to-lagoon-500" />
        </div>

        {/* Privacy Layer */}
        <div className="bg-mint-900/30 border border-mint-500/30 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-mint-500/20 border border-mint-500/50 flex items-center justify-center text-lg">
              🔐
            </div>
            <div>
              <p className="font-semibold text-mint-300">Privacy Layer — MIST.cash</p>
              <p className="text-sm text-slate-400">Unlinkable deposits & withdrawals</p>
            </div>
          </div>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <div className="w-0.5 h-6 bg-gradient-to-b from-mint-500 to-lagoon-500" />
        </div>

        {/* Verification Layer */}
        <div className="bg-lagoon-900/30 border border-lagoon-500/30 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-lagoon-500/20 border border-lagoon-500/50 flex items-center justify-center text-lg">
              🧠
            </div>
            <div>
              <p className="font-semibold text-lagoon-300">Verification Layer — Cairo + SHARP</p>
              <p className="text-sm text-slate-400">Risk engine runs in Cairo, SHARP proves correctness</p>
            </div>
          </div>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <div className="w-0.5 h-6 bg-gradient-to-b from-lagoon-500 to-slate-500" />
        </div>

        {/* Routing Layer */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-lg">
              🔄
            </div>
            <div>
              <p className="font-semibold text-white">Routing Layer — Strategy Router</p>
              <p className="text-sm text-slate-400">Verifiable allocation across protocols</p>
            </div>
          </div>
        </div>

        {/* Arrow with branching */}
        <div className="flex justify-center">
          <div className="w-0.5 h-4 bg-slate-600" />
        </div>

        {/* Protocol Layer */}
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-blue-900/30 border border-blue-500/30 rounded-xl p-3 text-center">
            <p className="font-semibold text-blue-300 text-sm">Nostra</p>
            <p className="text-xs text-slate-400">Lending</p>
          </div>
          <div className="bg-purple-900/30 border border-purple-500/30 rounded-xl p-3 text-center">
            <p className="font-semibold text-purple-300 text-sm">zkLend</p>
            <p className="text-xs text-slate-400">Money Market</p>
          </div>
          <div className="bg-orange-900/30 border border-orange-500/30 rounded-xl p-3 text-center">
            <p className="font-semibold text-orange-300 text-sm">Ekubo</p>
            <p className="text-xs text-slate-400">DEX / LP</p>
          </div>
        </div>

        {/* Arrow */}
        <div className="flex justify-center">
          <div className="w-0.5 h-4 bg-slate-600" />
        </div>

        {/* Yields */}
        <div className="bg-green-900/30 border border-green-500/30 rounded-xl p-4 text-center">
          <p className="font-semibold text-green-300">Verifiable Yields</p>
          <p className="text-xs text-slate-400">Private withdrawal via MIST</p>
        </div>
      </div>
    </div>
  );
}

function ComparisonDiagram({ className }: { className: string }) {
  return (
    <div className={`grid md:grid-cols-2 gap-4 ${className}`}>
      {/* EVM Side */}
      <div className="bg-slate-100 border border-slate-200 rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-3 h-3 rounded-full bg-red-400" />
          <h3 className="font-display text-lg text-ink">EVM Obsqra</h3>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="bg-white rounded-lg p-3 border border-slate-200">
            <p className="text-slate-600">User Deposit</p>
          </div>
          <div className="flex justify-center text-slate-400">↓</div>
          <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
            <p className="text-yellow-700">Privacy Pool (custom built)</p>
            <p className="text-xs text-yellow-600 mt-1">Months of dev work</p>
          </div>
          <div className="flex justify-center text-slate-400">↓</div>
          <div className="bg-red-50 rounded-lg p-3 border border-red-200">
            <p className="text-red-700">Risk Model (black box)</p>
            <p className="text-xs text-red-600 mt-1">Cannot be verified</p>
          </div>
          <div className="flex justify-center text-slate-400">↓</div>
          <div className="bg-white rounded-lg p-3 border border-slate-200">
            <p className="text-slate-600">Aave / Lido / Compound</p>
          </div>
          <div className="flex justify-center text-slate-400">↓</div>
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
            <p className="text-slate-500">Yields (trust required)</p>
          </div>
        </div>
      </div>

      {/* Starknet Side */}
      <div className="bg-gradient-to-b from-mint-50 to-lagoon-50 border border-mint-200 rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-3 h-3 rounded-full bg-green-400" />
          <h3 className="font-display text-lg text-ink">Starknet Obsqra</h3>
        </div>
        
        <div className="space-y-2 text-sm">
          <div className="bg-white rounded-lg p-3 border border-slate-200">
            <p className="text-slate-600">User Deposit</p>
          </div>
          <div className="flex justify-center text-mint-500">↓</div>
          <div className="bg-mint-100 rounded-lg p-3 border border-mint-300">
            <p className="text-mint-800 font-medium">MIST (native privacy)</p>
            <p className="text-xs text-mint-600 mt-1">Days of integration</p>
          </div>
          <div className="flex justify-center text-lagoon-500">↓</div>
          <div className="bg-lagoon-100 rounded-lg p-3 border border-lagoon-300">
            <p className="text-lagoon-800 font-medium">Cairo + SHARP (verifiable)</p>
            <p className="text-xs text-lagoon-600 mt-1">Proofs on-chain</p>
          </div>
          <div className="flex justify-center text-slate-400">↓</div>
          <div className="bg-white rounded-lg p-3 border border-slate-200">
            <p className="text-slate-600">Nostra / zkLend / Ekubo</p>
          </div>
          <div className="flex justify-center text-green-500">↓</div>
          <div className="bg-green-100 rounded-lg p-3 border border-green-300">
            <p className="text-green-800 font-medium">Verifiable Yields</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function FlowDiagram({ className }: { className: string }) {
  return (
    <div className={`bg-white border border-slate-200 rounded-2xl p-6 ${className}`}>
      <h3 className="font-display text-lg text-ink mb-4">Private Yield Flow</h3>
      
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Step 1 */}
        <div className="flex-1 text-center">
          <div className="w-12 h-12 rounded-full bg-mint-100 border-2 border-mint-300 flex items-center justify-center mx-auto mb-2">
            <span className="text-mint-700 font-bold">1</span>
          </div>
          <p className="font-semibold text-ink text-sm">Private Deposit</p>
          <p className="text-xs text-slate-500 mt-1">via MIST</p>
        </div>

        <div className="hidden md:block text-slate-300">→</div>

        {/* Step 2 */}
        <div className="flex-1 text-center">
          <div className="w-12 h-12 rounded-full bg-lagoon-100 border-2 border-lagoon-300 flex items-center justify-center mx-auto mb-2">
            <span className="text-lagoon-700 font-bold">2</span>
          </div>
          <p className="font-semibold text-ink text-sm">Risk Analysis</p>
          <p className="text-xs text-slate-500 mt-1">Cairo engine</p>
        </div>

        <div className="hidden md:block text-slate-300">→</div>

        {/* Step 3 */}
        <div className="flex-1 text-center">
          <div className="w-12 h-12 rounded-full bg-purple-100 border-2 border-purple-300 flex items-center justify-center mx-auto mb-2">
            <span className="text-purple-700 font-bold">3</span>
          </div>
          <p className="font-semibold text-ink text-sm">Proof Generation</p>
          <p className="text-xs text-slate-500 mt-1">SHARP attests</p>
        </div>

        <div className="hidden md:block text-slate-300">→</div>

        {/* Step 4 */}
        <div className="flex-1 text-center">
          <div className="w-12 h-12 rounded-full bg-blue-100 border-2 border-blue-300 flex items-center justify-center mx-auto mb-2">
            <span className="text-blue-700 font-bold">4</span>
          </div>
          <p className="font-semibold text-ink text-sm">Protocol Routing</p>
          <p className="text-xs text-slate-500 mt-1">Verifiable allocation</p>
        </div>

        <div className="hidden md:block text-slate-300">→</div>

        {/* Step 5 */}
        <div className="flex-1 text-center">
          <div className="w-12 h-12 rounded-full bg-green-100 border-2 border-green-300 flex items-center justify-center mx-auto mb-2">
            <span className="text-green-700 font-bold">5</span>
          </div>
          <p className="font-semibold text-ink text-sm">Private Withdraw</p>
          <p className="text-xs text-slate-500 mt-1">via MIST</p>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-100">
        <div className="flex flex-wrap justify-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-mint-300" />
            <span className="text-slate-600">Privacy (MIST)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-lagoon-300" />
            <span className="text-slate-600">Verification (Cairo)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-purple-300" />
            <span className="text-slate-600">Attestation (SHARP)</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ArchitectureDiagram;

