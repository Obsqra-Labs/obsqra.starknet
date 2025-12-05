'use client';

import { Dashboard } from '@/components/Dashboard';
import { useAccount, useConnect, useDisconnect } from '@starknet-react/core';

export default function Home() {
  const { address, account, status } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();

  if (status === 'disconnected') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center max-w-2xl px-6">
          <div className="mb-8">
            <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
              Obsqra.starknet
            </h1>
            <p className="text-2xl text-gray-300 mb-2">
              Verifiable AI Infrastructure for Private DeFi
            </p>
            <p className="text-gray-400">
              Connect your Starknet wallet to get started
            </p>
          </div>

          <div className="space-y-4">
            {connectors.map((connector) => (
              <button
                key={connector.id}
                onClick={() => connect({ connector })}
                disabled={!connector.available()}
                className={`
                  w-full px-8 py-4 rounded-xl font-semibold text-lg
                  transition-all transform hover:scale-105
                  ${connector.available()
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl'
                    : 'bg-gray-700 text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                {connector.available() ? (
                  `Connect ${connector.name}`
                ) : (
                  `${connector.name} Not Installed`
                )}
              </button>
            ))}
          </div>

          <div className="mt-8 text-sm text-gray-400">
            <p className="mb-2">Supported wallets:</p>
            <p>• Argent X • Braavos</p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'connecting' || status === 'reconnecting') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500 border-solid mx-auto mb-4"></div>
          <p className="text-xl text-gray-300">Connecting to wallet...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <nav className="bg-black/30 backdrop-blur-md border-b border-purple-500/20 shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
              Obsqra.starknet
            </h1>
            <div className="flex items-center gap-4">
              <div className="px-4 py-2 bg-purple-600/30 rounded-lg border border-purple-500/30">
                <span className="text-sm text-gray-300">
                  {address?.slice(0, 6)}...{address?.slice(-4)}
                </span>
              </div>
              <button
                onClick={() => disconnect()}
                className="px-4 py-2 bg-red-600/80 hover:bg-red-600 text-white rounded-lg transition font-medium"
              >
                Disconnect
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="container mx-auto py-8">
        <Dashboard />
      </main>
    </div>
  );
}
