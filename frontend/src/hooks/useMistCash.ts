import { useAccount, useProvider } from '@starknet-react/core';
import { useMemo } from 'react';
import { MistCashService } from '@/services/mist';

const MIST_CHAMBER_ADDRESS = process.env.NEXT_PUBLIC_MIST_CHAMBER_ADDRESS || '';

export function useMistCash() {
  const { account } = useAccount();
  const { provider } = useProvider();
  
  const mistService = useMemo(() => {
    if (!provider || !account) return null;
    return new MistCashService(provider, MIST_CHAMBER_ADDRESS);
  }, [provider, account]);
  
  return {
    mistService,
    isConnected: !!account,
  };
}

