# MIST.cash Quick Start

Get MIST privacy integrated into Obsqra in 5 minutes.

## 1. Install Dependencies

```bash
cd frontend
npm install
```

The following packages are now available:
- `@mistcash/sdk` - Core contract interactions
- `@mistcash/crypto` - Cryptographic operations
- `@mistcash/react` - React hooks
- `@mistcash/config` - ABIs and addresses

## 2. Configure Environment

Create/update `frontend/.env.local`:

```bash
# Get this from MIST team or @mistcash/config
NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=0x...

# These should already be configured
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_7/EvhYN6geLrdvbYHVRgPJ7
NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x01fa59cf9a28d97fd9ab5db1e21f9dd6438af06cc535bccdb58962518cfdf53a
```

## 3. Start Frontend

```bash
npm run dev
# http://localhost:3003
```

## 4. Test It

### Demo Mode (No Wallet Needed)
1. Open dashboard
2. Click "🎮 Demo Mode" toggle in header
3. Enter amount (e.g., "10")
4. Click "💰 Deposit Privately"
5. See claiming key generated
6. Check "📜 History" tab

### Live Mode (Testnet STRK Required)
1. Connect wallet (Argent X or Braavos)
2. Get testnet STRK: https://starknet-faucet.vercel.app/
3. Turn off demo mode
4. Click "💰 Deposit Privately"
5. Approve in wallet
6. Copy claiming key
7. View on Starkscan: https://sepolia.starkscan.co/

## 5. Key Files

| File | Purpose |
|------|---------|
| `src/services/mist.ts` | MIST protocol service |
| `src/hooks/useMistCash.ts` | React integration hook |
| `src/components/Dashboard.tsx` | Deposit/withdraw UI |
| `docs/MIST_INTEGRATION.md` | Full documentation |

## API Overview

### Deposit (Private)

```typescript
import { useMistCash } from '@/hooks/useMistCash';

const { mistService, isReady } = useMistCash();

// Create private deposit
const amount = BigInt(50 * 1e18); // 50 STRK
const claimingKey = 'mist_' + Date.now() + '_' + randomKey();
const txHash = await mistService.deposit(amount, recipientAddress, claimingKey);

// Share claimingKey with recipient
```

### Withdraw (Using Claiming Key)

```typescript
// Recipient uses claiming key to withdraw
const txHash = await mistService.withdraw(claimingKey, recipientAddress, amount);
```

### Check Transaction Exists

```typescript
const exists = await mistService.checkTransactionExists(
  claimingKey,
  recipientAddress,
  tokenAddress,
  amount
);
```

## Features

✅ Private deposits with claiming key  
✅ Unlinkable transactions (sender-receiver not linked)  
✅ Full error handling  
✅ Demo mode for testing  
✅ Transaction history  
✅ Claiming key management  
✅ Type-safe TypeScript  
✅ Mainnet ready  

## Troubleshooting

**"Module not found"**
```bash
npm install
```

**"Chamber address is not set"**
- Set `NEXT_PUBLIC_MIST_CHAMBER_ADDRESS` in `.env.local`
- Get address from MIST team

**Transactions fail in live mode**
- Ensure wallet connected
- Check testnet STRK balance
- Verify chamber address is correct

## What is MIST?

MIST.cash is a Starknet privacy protocol that enables:

- **Unlinkable sends** - No on-chain link between sender and receiver
- **Claiming keys** - Recipient uses key to redeem funds
- **Full privacy** - Amounts and recipients can be private

## Resources

- SDK: https://github.com/mistcash/sdk
- Full Guide: [docs/MIST_INTEGRATION.md](MIST_INTEGRATION.md)
- Starknet Faucet: https://starknet-faucet.vercel.app/
- Starkscan: https://sepolia.starkscan.co/

---

Ready to send private transactions! 

