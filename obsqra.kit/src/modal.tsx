// @ts-nocheck
'use client';

import type { CSSProperties } from 'react';
import { useWalletKit } from './useWalletKit';

interface WalletModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
}

export function WalletModal({
  open,
  onClose,
  title = 'Connect a Starknet wallet',
  description = 'Choose a wallet to continue. Argent X and Braavos are supported out of the box.',
}: WalletModalProps) {
  const {
    connectors,
    connect,
    status,
    error,
    preferredConnector,
    wrongNetwork,
    chainName,
    expectedChainName,
    canSwitchNetwork,
    switchNetwork,
  } = useWalletKit();

  if (!open) return null;

  const overlayStyle: CSSProperties = {
    position: 'fixed',
    inset: 0,
    background: 'rgba(15, 23, 42, 0.55)',
    backdropFilter: 'blur(6px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  };

  const cardStyle: CSSProperties = {
    width: 'min(420px, 92vw)',
    background: '#ffffff',
    borderRadius: '20px',
    boxShadow: '0 20px 80px rgba(0,0,0,0.2)',
    padding: '24px',
    border: '1px solid rgba(0,0,0,0.06)',
  };

  const buttonStyle: CSSProperties = {
    width: '100%',
    padding: '12px 14px',
    borderRadius: '12px',
    border: '1px solid rgba(0,0,0,0.08)',
    background: '#f8fafc',
    color: '#0f172a',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    cursor: 'pointer',
    transition: 'all 0.15s ease',
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={cardStyle} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>{title}</div>
            <div style={{ fontSize: '13px', color: '#475569', marginTop: '4px' }}>{description}</div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close wallet modal"
            style={{
              border: '1px solid rgba(0,0,0,0.08)',
              background: '#f8fafc',
              borderRadius: '999px',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
            }}
          >
            ×
          </button>
        </div>

        {wrongNetwork && (
          <div
            style={{
              marginTop: '12px',
              padding: '10px',
              borderRadius: '10px',
              background: 'rgba(234,179,8,0.12)',
              color: '#92400e',
              fontSize: '13px',
              border: '1px solid rgba(234,179,8,0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '10px',
            }}
          >
            <span>
              You&apos;re on {chainName || 'an unknown network'}. Please switch to {expectedChainName || 'the expected network'}.
            </span>
            {canSwitchNetwork && (
              <button
                onClick={() => switchNetwork()}
                style={{
                  padding: '8px 10px',
                  borderRadius: '10px',
                  border: '1px solid rgba(234,179,8,0.3)',
                  background: '#fef3c7',
                  color: '#92400e',
                  cursor: 'pointer',
                  fontWeight: 700,
                  fontSize: '12px',
                }}
              >
                Switch
              </button>
            )}
          </div>
        )}

        <div style={{ marginTop: '16px', display: 'grid', gap: '10px' }}>
          {connectors.map((connector) => {
            const available = connector.available();
            const isPreferred = preferredConnector?.id === connector.id;

            return (
              <button
                key={connector.id}
                onClick={() => connect(connector)}
                disabled={!available || status === 'connecting'}
                style={{
                  ...buttonStyle,
                  opacity: available ? 1 : 0.5,
                  cursor: available ? 'pointer' : 'not-allowed',
                  borderColor: isPreferred ? 'rgba(16, 185, 129, 0.25)' : buttonStyle.border as string,
                  boxShadow: isPreferred ? '0 0 0 3px rgba(16, 185, 129, 0.15)' : 'none',
                }}
              >
                <span>{connector.name}</span>
                <span style={{ fontSize: '12px', color: '#475569' }}>
                  {available ? (isPreferred ? 'Preferred' : 'Available') : 'Not installed'}
                </span>
              </button>
            );
          })}
        </div>

        {error && (
          <div
            style={{
              marginTop: '12px',
              padding: '10px',
              borderRadius: '10px',
              background: 'rgba(239, 68, 68, 0.08)',
              color: '#b91c1c',
              fontSize: '13px',
              border: '1px solid rgba(239, 68, 68, 0.15)',
            }}
          >
            {error}
          </div>
        )}

        <p style={{ marginTop: '14px', fontSize: '12px', color: '#64748b' }}>
          New connectors? Pass them into `WalletKitProvider`. Built by Obsqra Labs for the Starknet community.
        </p>
      </div>
    </div>
  );
}
