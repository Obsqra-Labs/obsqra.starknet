'use client';

import { StarknetConfig, publicProvider } from '@starknet-react/core';
import { getInstalledInjectedConnectors } from '@starknet-react/core';
import { ReactNode } from 'react';

export function StarknetProvider({ children }: { children: ReactNode }) {
  const connectors = getInstalledInjectedConnectors();
  const provider = publicProvider();

  return (
    <StarknetConfig
      connectors={connectors}
      provider={provider}
    >
      {children}
    </StarknetConfig>
  );
}

