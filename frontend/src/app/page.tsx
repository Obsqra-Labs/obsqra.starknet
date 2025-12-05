'use client';

import { useAccount, useConnect } from '@starknet-react/core';

export default function Home() {
  const { account, address } = useAccount();
  const { connect, connectors } = useConnect();

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Obsqra.starknet Dashboard</h1>
      
      {!account ? (
        <div>
          <p className="mb-4">Connect your wallet to get started</p>
          {connectors.map((connector) => (
            <button
              key={connector.id}
              onClick={() => connect({ connector })}
              className="px-4 py-2 bg-blue-500 text-white rounded mr-2"
            >
              Connect {connector.name}
            </button>
          ))}
        </div>
      ) : (
        <div>
          <p>Connected: {address}</p>
          <p className="mt-4">Dashboard coming soon...</p>
        </div>
      )}
    </div>
  );
}

