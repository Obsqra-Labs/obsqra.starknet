'use client';

import { useAccount, useConnect } from '@starknet-react/core';
import { Dashboard } from '@/components/Dashboard';

export default function Home() {
  const { account } = useAccount();
  const { connect, connectors } = useConnect();

  if (!account) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-6">Obsqra.starknet</h1>
          <p className="text-xl mb-8">Verifiable AI Infrastructure for Private DeFi</p>
          <p className="mb-4">Connect your wallet to get started</p>
          <div className="space-x-4">
            {connectors.map((connector) => (
              <button
                key={connector.id}
                onClick={() => connect({ connector })}
                className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
              >
                Connect {connector.name}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold">Obsqra.starknet</h1>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {account.address.slice(0, 6)}...{account.address.slice(-4)}
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
