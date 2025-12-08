'use client';

import { Chain } from '@starknet-react/chains';
import { ReactNode, useMemo } from 'react';
import { WalletKitProvider } from 'obsqra.kit';

// Default Sepolia chain (can be overridden via prop)
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
  // Prefer production proxy when served over https to avoid CORS; otherwise use env or fallback RPC.
  const rpcUrl = useMemo(() => {
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      return '/api/rpc';
    }
    return process.env.NEXT_PUBLIC_STARKNET_RPC || 'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7';
  }, []);

  return (
    <WalletKitProvider chains={[sepoliaCustom]} rpcUrl={rpcUrl} autoConnect>
      {children}
    </WalletKitProvider>
  );
}
