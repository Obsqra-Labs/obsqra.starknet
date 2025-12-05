'use client';

import { StarknetConfig, argent, braavos, useInjectedConnectors, jsonRpcProvider } from '@starknet-react/core';
import { sepolia, mainnet } from '@starknet-react/chains';
import { ReactNode } from 'react';

export function StarknetProvider({ children }: { children: ReactNode }) {
  const { connectors } = useInjectedConnectors({
    recommended: [argent(), braavos()],
    includeRecommended: 'onlyIfNoConnectors',
    order: 'random',
  });

  // Provider factory function for each chain
  const provider = jsonRpcProvider({
    rpc: (chain) => {
      // Return appropriate RPC URL for each chain
      if (chain.id === sepolia.id) {
        return {
          nodeUrl: process.env.NEXT_PUBLIC_RPC_URL || 'https://starknet-sepolia.public.blastapi.io/rpc/v0_7',
        };
      }
      // Fallback for mainnet or other chains
      return {
        nodeUrl: 'https://starknet-mainnet.public.blastapi.io/rpc/v0_7',
      };
    },
  });

  return (
    <StarknetConfig
      chains={[sepolia, mainnet]}
      provider={provider}
      connectors={connectors}
      autoConnect
    >
      {children}
    </StarknetConfig>
  );
}

