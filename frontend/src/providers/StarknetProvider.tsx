'use client';

import { Chain, sepolia } from '@starknet-react/chains';
import { ReactNode } from 'react';
import { StarknetConfig, publicProvider } from '@starknet-react/core';
import { argentPatched, braavosPatched } from '@/lib/patchedConnectors';

// Create custom Sepolia chain with reliable Alchemy RPC
// Use spread operator to preserve all properties, then override rpcUrls
const sepoliaCustom: Chain = {
  ...sepolia,
  rpcUrls: {
    default: {
      http: ['https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7'],
    },
    public: {
      http: ['https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7'],
    },
  },
};

export function StarknetProvider({ children }: { children: ReactNode }) {
  // Use custom chain with reliable Alchemy RPC
  const provider = publicProvider();
  const chains = [sepoliaCustom];
  const connectors = [argentPatched(), braavosPatched()];

  return (
    <StarknetConfig chains={chains} provider={provider} connectors={connectors} autoConnect>
      {children}
    </StarknetConfig>
  );
}
