# Obsqra Kit — Starknet Wallet UX

Open-source wallet kit from Obsqra Labs. It powers the Starknet experience on `starknet.obsqra.fi` and is ready for any dApp that wants a consistent, proof-friendly wallet flow.

- Headless hooks on `@starknet-react/core` / `starknet`
- Optional Rainbow-style modal for Argent X and Braavos (extensible)
- Presets for Starknet Sepolia/Mainnet RPC + expected-network guard rails
- Persistence for last-used connector + friendly error states

We’re grateful to the Starknet community—contributions and forks welcome.

## Why this exists
Starknet has great primitives but no widely adopted, polished multi-wallet UX (RainbowKit equivalent). This kit packages the basics so teams can ship faster and keep users in flow.

## Install
```bash
# from your app
npm install obsqra.kit @starknet-react/core @starknet-react/chains starknet react
# or
pnpm add obsqra.kit @starknet-react/core @starknet-react/chains starknet react
```

## Quickstart
Wrap your app once, then use the hook everywhere.

```tsx
// app/providers.tsx
import { WalletKitProvider } from 'obsqra.kit';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WalletKitProvider>
      {children}
    </WalletKitProvider>
  );
}
```

Consume in a component:
```tsx
import { useWalletKit, WalletModal } from 'obsqra.kit';
import { useState } from 'react';

export function ConnectButton() {
  const { address, status, connect, disconnect, connectors, preferredConnector } = useWalletKit();
  const [open, setOpen] = useState(false);

  if (status === 'connected') {
    return (
      <button onClick={disconnect}>
        Disconnect {address?.slice(0, 6)}...
      </button>
    );
  }

  return (
    <>
      <button onClick={() => (preferredConnector ? connect(preferredConnector) : setOpen(true))}>
        {status === 'connecting' ? 'Connecting…' : 'Connect wallet'}
      </button>
      <WalletModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
```

## Configuration
`WalletKitProvider` props (all optional):
- `chains`: array of Starknet chains (defaults include Sepolia preset)
- `rpcUrl`: override RPC for presets (e.g., Alchemy/Infura/custom)
- `connectors`: provide your own connectors; otherwise Argent/Braavos injected are used
- `autoConnect`: default `true` (reconnects using last connector if available)
- `expectedChainId` / `expectedChainName`: set the network you expect; the hook surfaces `wrongNetwork` for UX prompts

Example with custom RPC:
```tsx
<WalletKitProvider rpcUrl={process.env.NEXT_PUBLIC_STARKNET_RPC}>
  {children}
</WalletKitProvider>
```

## API
`useWalletKit()` returns:
- `address`, `status` (`'disconnected' | 'connecting' | 'connected' | 'reconnecting'`)
- `connect(connector?)`, `disconnect()`
- `connectors`: available connectors
- `preferredConnector`: best available (last used > available > first)
- `lastConnectorId`: id stored in `localStorage`
- `chainId`, `chainName`, `expectedChainId`, `expectedChainName`, `wrongNetwork`
- `error`: last connect error (normalized string)

`WalletModal`:
- Props: `open: boolean`, `onClose: () => void`, optional `title?: string`, `description?: string`
- Renders available connectors, shows availability and errors.

## Extending
- Add more connectors (hardware/embedded/QR) by passing `connectors` into the provider.
- The modal is intentionally simple; theme it with your design system or swap in your own UI while keeping `useWalletKit`.
- Build proof-aware UX: subscribe to contract events and show SHARP proof hashes next to wallet state (we’ll add helpers in follow-ups).

## Roadmap
- QR / deep-link flows when Starknet kit support lands
- Network switch prompt + chain guard rails (in progress)
- Storybook examples + unit tests
- Proof helpers for Cairo/SHARP display

## Contributing
MIT licensed. Please open issues/PRs—especially around connectors, UX polish, and QR flows. Built by Obsqra Labs; thanks to everyone shipping on Starknet.
