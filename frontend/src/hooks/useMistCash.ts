'use client';

import { useMemo } from 'react';
import { useAccount, useProvider } from '@starknet-react/core';
import { MistCashService } from '@/services/mist';

/**
 * Hook to interact with MIST.cash privacy protocol
 */
export function useMistCash() {
  const { account, address, status } = useAccount();
  const { provider } = useProvider();

  const chamberAddress = process.env.NEXT_PUBLIC_MIST_CHAMBER_ADDRESS || '';

  const mistService = useMemo(() => {
    if (!provider || !chamberAddress) return null;
    return new MistCashService(provider, chamberAddress);
  }, [provider, chamberAddress]);

  const isConnected = status === 'connected' && !!account && !!address;

  return {
    mistService,
    isConnected,
    chamberAddress,
  };
}
