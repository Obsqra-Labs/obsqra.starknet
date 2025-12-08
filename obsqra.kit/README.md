# Obsqra Kit — Starknet wallet toolkit

Open-source, app-agnostic wallet kit for Starknet. Built to be the RainbowKit-style starting point the ecosystem is missing—plug it into any dApp, or theme it to your design system.

- Headless hooks on `@starknet-react/core` / `starknet`
- Lightweight modal + plug-and-play buttons for Argent X and Braavos (extensible)
- Presets for Starknet Sepolia/Mainnet RPC and expected-network guard rails
- Persists last-used connector; exposes normalized errors and wrong-network state

Built by Obsqra Labs for the community; contributions and forks welcome.

## Install
```bash
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

Use the headless hook or the prebuilt button/modal:
```tsx
import { useWalletKit, WalletModal, ConnectButton, AccountChip } from 'obsqra.kit';
import { useState } from 'react';

export function ConnectButton() {
  const { address, status, connect, disconnect, connectors, preferredConnector } = useWalletKit();
  const [open, setOpen] = useState(false);

  if (status === 'connected') {
    return (
      <>
        <AccountChip />
        <button onClick={disconnect}>Disconnect {address?.slice(0, 6)}...</button>
      </>
    );
  }

  return (
    <>
      <ConnectButton />
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
- `onConnect` / `onDisconnect` (coming soon): side-effect callbacks

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
- `canSwitchNetwork`, `switchNetwork(targetId?)`, `switchNetworkAsync(targetId?)`
- `error`: last connect error (normalized string)

`WalletModal`:
- Props: `open: boolean`, `onClose: () => void`, optional `title?: string`, `description?: string`
- Renders available connectors, shows availability and errors, and offers network switch when `expectedChainId` is set.

UI helpers:
- `ConnectButton`: one-line “connect” that auto-uses preferred connector or opens the modal.
- `AccountChip`: shows address + network badge, with wrong-network switch prompt and a disconnect button.

## Extending
- Add more connectors (hardware/embedded/QR) by passing `connectors` into the provider.
- The modal is intentionally simple; theme it with your design system or swap in your own UI while keeping `useWalletKit`.
- Build proof-aware UX: subscribe to contract events and show SHARP proof hashes next to wallet state (we’ll add helpers in follow-ups).

## Roadmap
- Theming tokens + light/dark presets
- QR / deep-link flows (WalletConnect when Starknet support is stable)
- Network switch prompt (shipping now) + chain selector presets
- Storybook examples + unit tests
- Proof helpers for Cairo/SHARP display

## Contributing
MIT licensed. Please open issues/PRs—especially around connectors, UX polish, and QR flows. Built by Obsqra Labs; thanks to everyone shipping on Starknet.
