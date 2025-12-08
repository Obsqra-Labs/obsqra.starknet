'use client';

import { StarknetConfig, argent, braavos, useInjectedConnectors, jsonRpcProvider } from '@starknet-react/core';
import { Chain } from '@starknet-react/chains';
import { ReactNode } from 'react';

// Define custom Sepolia chain with Alchemy RPC to avoid CORS issues
const sepoliaCustom: Chain = {
  id: BigInt('0x534e5f5345504f4c4941'), // SN_SEPOLIA
  network: 'sepolia',
  name: 'Starknet Sepolia',
  nativeCurrency: {
    address: '0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1',
    name: 'Ether',
    symbol: 'ETH',
    decimals: 18,
  },
  testnet: true,
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
  const { connectors } = useInjectedConnectors({
    recommended: [argent(), braavos()],
    includeRecommended: 'onlyIfNoConnectors',
    order: 'random',
  });

  // Provider factory function - use local proxy to avoid CORS issues
  const provider = jsonRpcProvider({
    rpc: (chain) => {
      // In production, use local proxy endpoint; in dev, use direct RPC
      const isProduction = typeof window !== 'undefined' && window.location.protocol === 'https:';
      const nodeUrl = isProduction
        ? '/api/rpc'  // Local proxy endpoint
        : 'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7'; // Direct RPC for local dev
      
      return { nodeUrl };
    },
  });

  return (
    <StarknetConfig
      chains={[sepoliaCustom]}
      provider={provider}
      connectors={connectors}
      autoConnect
    >
      {children}
    </StarknetConfig>
  );
}

