// @ts-nocheck
'use client';

import { ReactNode, useEffect, useMemo } from 'react';
import { StarknetConfig, argent, braavos, jsonRpcProvider, useInjectedConnectors } from '@starknet-react/core';
import { Chain } from '@starknet-react/chains';
import { WalletKitStateProvider } from './useWalletKit';

export interface WalletKitProviderProps {
  children: ReactNode;
  chains?: Chain[];
  rpcUrl?: string;
  connectors?: ReturnType<typeof useInjectedConnectors>['connectors'];
  autoConnect?: boolean;
  expectedChainId?: bigint;
  expectedChainName?: string;
}

const STARKNET_SEPOLIA: Chain = {
  id: BigInt('0x534e5f5345504f4c4941'),
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
      http: ['https://starknet-sepolia.public.blastapi.io'],
    },
    public: {
      http: ['https://starknet-sepolia.public.blastapi.io'],
    },
  },
};

export function WalletKitProvider({
  children,
  chains,
  rpcUrl,
  connectors,
  autoConnect = true,
  expectedChainId,
  expectedChainName,
}: WalletKitProviderProps) {
  useEffect(() => {
    console.info('[obsqra.kit] WalletKitProvider mounted (Argent/Braavos, Sepolia preset)');
  }, []);

  const { connectors: injectedConnectors } = useInjectedConnectors({
    recommended: [argent(), braavos()],
    includeRecommended: 'onlyIfNoConnectors',
    order: 'random',
  });

  const activeChains = chains ?? [STARKNET_SEPOLIA];
  const activeConnectors = connectors ?? injectedConnectors;

  const provider = useMemo(
    () =>
      jsonRpcProvider({
        rpc: () => ({
          nodeUrl:
            rpcUrl ||
            process.env.NEXT_PUBLIC_STARKNET_RPC ||
            'https://starknet-sepolia.public.blastapi.io',
        }),
      }),
    [rpcUrl],
  );

  return (
    <StarknetConfig
      chains={activeChains}
      provider={provider}
      connectors={activeConnectors}
      autoConnect={autoConnect}
    >
      <WalletKitStateProvider
        expectedChainId={expectedChainId ?? activeChains[0]?.id}
        expectedChainName={expectedChainName ?? activeChains[0]?.name}
      >
        {children}
      </WalletKitStateProvider>
    </StarknetConfig>
  );
}
