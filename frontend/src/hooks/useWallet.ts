'use client';

import { useAccount, useConnect, useDisconnect } from '@starknet-react/core';
import { Connector } from '@starknet-react/core';
import { useCallback, useMemo } from 'react';

export interface UseWalletReturn {
  address?: string;
  isConnected: boolean;
  isConnecting: boolean;
  connectors: Connector[];
  preferredConnector?: Connector;
  connect: (connector?: Connector) => Promise<void>;
  disconnect: () => Promise<void>;
  error: string | null;
  clearError: () => void;
  wrongNetwork: boolean;
  chainName?: string;
  expectedChainName?: string;
}

export function useWallet(): UseWalletReturn {
  const { address, isConnected } = useAccount();
  const { connect: starknetConnect, connectors, isPending: isConnecting, error } = useConnect();
  const { disconnect: starknetDisconnect } = useDisconnect();

  const connect = useCallback(
    async (connector?: Connector) => {
      if (connector) {
        await starknetConnect({ connector });
      }
    },
    [starknetConnect]
  );

  const disconnect = useCallback(async () => {
    await starknetDisconnect();
  }, [starknetDisconnect]);

  const preferredConnector = useMemo(() => {
    // Try to find Argent first, then Braavos
    return connectors.find((c) => c.id === 'argentX') || connectors.find((c) => c.id === 'braavos');
  }, [connectors]);

  return {
    address,
    isConnected,
    isConnecting,
    connectors,
    preferredConnector,
    connect,
    disconnect,
    error: error?.message || null,
    clearError: () => {
      // Errors are managed by the hook, no manual clear needed
    },
    wrongNetwork: false, // Starknet is single-chain, so no wrong network
    chainName: 'Starknet Sepolia',
    expectedChainName: 'Starknet Sepolia',
  };
}

