// Lightweight UI helpers to make the kit usable out of the box.
// These are intentionally style-lite; teams can theme or replace them.

'use client';

import { useState } from 'react';
import { useWalletKit } from './useWalletKit';
import { WalletModal } from './modal';

interface ConnectButtonProps {
  connectLabel?: string;
  disconnectLabel?: string;
  showAddress?: boolean;
}

export function ConnectButton({
  connectLabel = 'Connect wallet',
  disconnectLabel = 'Disconnect',
  showAddress = true,
}: ConnectButtonProps) {
  const { address, status, isConnected, connect, disconnect, preferredConnector, wrongNetwork } = useWalletKit();
  const [open, setOpen] = useState(false);

  if (isConnected) {
    const short = showAddress && address ? `${address.slice(0, 6)}…${address.slice(-4)}` : 'Connected';
    return (
      <button
        onClick={disconnect}
        style={{
          padding: '10px 14px',
          borderRadius: '12px',
          border: '1px solid rgba(0,0,0,0.08)',
          background: wrongNetwork ? '#fff7ed' : '#0f172a',
          color: wrongNetwork ? '#b45309' : '#f8fafc',
          fontWeight: 700,
          cursor: 'pointer',
        }}
      >
        {disconnectLabel} {short ? `(${short})` : ''}
      </button>
    );
  }

  const label = status === 'connecting' ? 'Connecting…' : connectLabel;

  return (
    <>
      <button
        onClick={() => (preferredConnector ? connect(preferredConnector) : setOpen(true))}
        style={{
          padding: '10px 14px',
          borderRadius: '12px',
          border: '1px solid rgba(0,0,0,0.08)',
          background: '#0f172a',
          color: '#f8fafc',
          fontWeight: 700,
          cursor: 'pointer',
        }}
      >
        {label}
      </button>
      <WalletModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}

interface AccountChipProps {
  showDisconnect?: boolean;
}

export function AccountChip({ showDisconnect = true }: AccountChipProps) {
  const { address, isConnected, disconnect, chainName, wrongNetwork, switchNetwork, expectedChainName } = useWalletKit();

  if (!isConnected || !address) return null;
  const short = `${address.slice(0, 6)}…${address.slice(-4)}`;

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '10px',
        padding: '10px 12px',
        borderRadius: '14px',
        border: '1px solid rgba(0,0,0,0.1)',
        background: '#f8fafc',
      }}
    >
      <span style={{ fontWeight: 700, color: '#0f172a' }}>{short}</span>
      <span style={{ fontSize: '12px', color: '#475569' }}>{chainName || 'Unknown network'}</span>
      {wrongNetwork && (
        <button
          onClick={() => switchNetwork()}
          style={{
            padding: '6px 8px',
            borderRadius: '10px',
            border: '1px solid rgba(248,113,113,0.4)',
            background: '#fef2f2',
            color: '#b91c1c',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Switch to {expectedChainName || 'expected'}
        </button>
      )}
      {showDisconnect && (
        <button
          onClick={disconnect}
          style={{
            padding: '6px 8px',
            borderRadius: '10px',
            border: '1px solid rgba(0,0,0,0.08)',
            background: '#e2e8f0',
            color: '#0f172a',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          Disconnect
        </button>
      )}
    </div>
  );
}
