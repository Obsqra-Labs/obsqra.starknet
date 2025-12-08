'use client';

import { useMemo } from 'react';
import { useAccount, useProvider } from '@starknet-react/core';
import { MistCashService } from '@/services/mist';

/**
 * Hook to interact with MIST.cash privacy protocol
 * Provides access to MIST deposit/withdraw operations and transaction verification
 */
export function useMistCash() {
  const { account, address, status } = useAccount();
  const { provider } = useProvider();

  // Get chamber address from environment or use default Sepolia address
  // For mainnet, update NEXT_PUBLIC_MIST_CHAMBER_ADDRESS in environment
  const chamberAddress = process.env.NEXT_PUBLIC_MIST_CHAMBER_ADDRESS || '';

  const mistService = useMemo(() => {
    if (!provider || !chamberAddress) {
      console.warn('MIST service not initialized: provider or chamber address missing');
      return null;
    }
    return new MistCashService(provider, chamberAddress, account);
  }, [provider, chamberAddress, account]);

  const isConnected = status === 'connected' && !!account && !!address;
  const isReady = isConnected && !!mistService;

  return {
    mistService,
    isConnected,
    isReady,
    chamberAddress,
    userAddress: address,
    account,
  };
}
