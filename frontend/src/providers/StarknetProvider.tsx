'use client';

import { Chain, sepolia } from '@starknet-react/chains';
import { ReactNode, useMemo } from 'react';
import { StarknetConfig, publicProvider, argent, braavos, connect, disconnect } from '@starknet-react/core';

export function StarknetProvider({ children }: { children: ReactNode }) {
  // Prefer production proxy when served over https to avoid CORS; otherwise use env or fallback RPC.
  const rpcUrl = useMemo(() => {
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      return '/api/rpc';
    }
    return process.env.NEXT_PUBLIC_STARKNET_RPC || 'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7';
  }, []);

  const chains = [sepolia];
  const provider = publicProvider();
  const connectors = [argent(), braavos()];

  return (
    <StarknetConfig chains={chains} provider={provider} connectors={connectors} autoConnect>
      {children}
    </StarknetConfig>
  );
}
