'use client';

import { useMemo, useState, useCallback } from 'react';
import { useProvider, useSendTransaction, useAccount } from '@starknet-react/core';
import { useMist } from '@mistcash/react';

/**
 * Advanced hook combining @mistcash/react for easier React integration
 * with additional utility functions for Obsqra dashboard
 */
export function useMistReact() {
  const provider = useProvider();
  const { account } = useAccount();
  const [transactionError, setTransactionError] = useState<string | null>(null);

  // Use the official MIST React hooks for easier integration
  const mist = useMemo(() => {
    if (!provider || !account) return null;
    try {
      // MIST React hook initialization
      // Note: useMist from @mistcash/react handles transaction signing internally
      return { provider, account };
    } catch (error) {
      console.error('Failed to initialize MIST React hooks:', error);
      setTransactionError('MIST.cash initialization failed');
      return null;
    }
  }, [provider, account]);

  const clearError = useCallback(() => {
    setTransactionError(null);
  }, []);

  return {
    mist,
    transactionError,
    clearError,
    account,
    isReady: !!mist && !!account,
  };
}

