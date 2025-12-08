// @ts-nocheck
'use client';

import {
  useAccount,
  useConnect,
  useDisconnect,
  useNetwork,
} from '@starknet-react/core';
import { ReactNode, createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

type Connector = ReturnType<typeof useConnect>['connectors'][number];

export type WalletStatus = ReturnType<typeof useAccount>['status'];

export interface WalletKitValue {
  address?: string;
  status: WalletStatus;
  isConnected: boolean;
  isConnecting: boolean;
  chainId?: bigint;
  chainName?: string;
  expectedChainId?: bigint;
  expectedChainName?: string;
  wrongNetwork: boolean;
  connectors: Connector[];
  preferredConnector?: Connector;
  lastConnectorId: string | null;
  connect: (connector?: Connector) => Promise<void>;
  disconnect: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const LAST_CONNECTOR_KEY = 'obsqra.wallet.lastConnector';

const WalletKitContext = createContext<WalletKitValue | undefined>(undefined);

function normalizeError(err: unknown): string {
  const message = err instanceof Error ? err.message : `${err ?? 'Unknown error'}`;
  if (/user (rejected|abort|canceled)/i.test(message)) return 'Connection canceled';
  if (/not installed|no .*wallet/i.test(message)) return 'Wallet not installed';
  if (/network|chain/i.test(message) && /unsupported/i.test(message)) return 'Unsupported network';
  return message;
}

export interface WalletKitStateProviderProps {
  children: ReactNode;
  expectedChainId?: bigint;
  expectedChainName?: string;
}

export function WalletKitStateProvider({
  children,
  expectedChainId,
  expectedChainName,
}: WalletKitStateProviderProps) {
  const { address, status } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();
  const { chain } = useNetwork();

  const [error, setError] = useState<string | null>(null);
  const [lastConnectorId, setLastConnectorId] = useState<string | null>(null);

  // Load last connector on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const stored = window.localStorage.getItem(LAST_CONNECTOR_KEY);
    if (stored) setLastConnectorId(stored);
  }, []);

  const preferredConnector = useMemo(() => {
    const fromLast = connectors.find((c) => c.id === lastConnectorId && c.available());
    if (fromLast) return fromLast;
    const firstAvailable = connectors.find((c) => c.available());
    if (firstAvailable) return firstAvailable;
    return connectors[0];
  }, [connectors, lastConnectorId]);

  const connectWallet = useCallback(
    async (connector?: Connector) => {
      const chosen = connector ?? preferredConnector;
      if (!chosen) {
        setError('No wallet connector available');
        return;
      }

      try {
        setError(null);
        await connect({ connector: chosen });
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(LAST_CONNECTOR_KEY, chosen.id);
        }
        setLastConnectorId(chosen.id);
      } catch (err) {
        setError(normalizeError(err));
      }
    },
    [connect, preferredConnector],
  );

  const disconnectWallet = useCallback(async () => {
    try {
      setError(null);
      await disconnect();
    } catch (err) {
      setError(normalizeError(err));
    }
  }, [disconnect]);

  const clearError = useCallback(() => setError(null), []);

  const chainId = chain?.id;
  const chainName = chain?.name;
  const wrongNetwork = expectedChainId ? !!chainId && chainId !== expectedChainId : false;

  const value: WalletKitValue = useMemo(
    () => ({
      address,
      status,
      isConnected: status === 'connected',
      isConnecting: status === 'connecting' || status === 'reconnecting',
      chainId,
      chainName,
      expectedChainId,
      expectedChainName,
      wrongNetwork,
      connectors,
      preferredConnector,
      lastConnectorId,
      connect: connectWallet,
      disconnect: disconnectWallet,
      error,
      clearError,
    }),
    [
      address,
      status,
      chainId,
      chainName,
      expectedChainId,
      expectedChainName,
      wrongNetwork,
      connectors,
      preferredConnector,
      lastConnectorId,
      connectWallet,
      disconnectWallet,
      error,
      clearError,
    ],
  );

  return (
    <WalletKitContext.Provider value={value}>
      {children}
    </WalletKitContext.Provider>
  );
}

export function useWalletKit(): WalletKitValue {
  const ctx = useContext(WalletKitContext);
  if (!ctx) {
    throw new Error('useWalletKit must be used within WalletKitProvider');
  }
  return ctx;
}
