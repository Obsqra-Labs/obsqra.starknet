# MIST.cash Integration Guide

## Overview

Obsqra.starknet integrates **MIST.cash**, a privacy-focused payment protocol on Starknet, to enable **unlinkable private deposits and withdrawals** for yield optimization strategies.

### What is MIST.cash?

MIST.cash is a Starknet-native privacy protocol that enables:
- **Unlinkable transactions** - No on-chain link between sender and receiver
- **Private payments** - Transaction amounts can be kept private
- **Claim-based model** - Recipient uses a claiming key to redeem funds

Reference: [MIST.cash SDK GitHub](https://github.com/mistcash/sdk)

---

## Architecture

```
Frontend (Next.js)
    ↓
useMistCash Hook
    ↓
MistCashService (src/services/mist.ts)
    ↓
@mistcash/sdk, @mistcash/crypto
    ↓
MIST Chamber Contract (Starknet)
    ↓
STRK Token Smart Contracts
```

---

## Implementation Details

### 1. **Dependencies**

The frontend uses the official MIST.cash SDK packages:

```json
{
  "@mistcash/config": "^0.2.0-beta.1",
  "@mistcash/crypto": "^0.2.0-beta.1",
  "@mistcash/react": "^0.2.0-beta.1",
  "@mistcash/sdk": "^0.2.0-beta.1"
}
```

### 2. **Core Service: MistCashService**

**Location**: `src/services/mist.ts`

Main methods:

#### `deposit(amount: bigint, recipientAddress: string, claimingKey: string): Promise<string>`

Creates a private deposit transaction:

```typescript
import { useMistCash } from '@/hooks/useMistCash';

const { mistService, isReady } = useMistCash();

// Create private deposit
const amount = BigInt(100 * 1e18); // 100 STRK
const claimingKey = 'mist_' + Date.now() + '_' + randomKey();
const txHash = await mistService.deposit(amount, recipientAddress, claimingKey);

// Share claiming key with recipient (securely)
```

**What happens:**
1. Generates transaction secret from claiming key
2. Submits deposit to MIST Chamber contract
3. Creates unlinkable transaction
4. Returns transaction hash for tracking

#### `withdraw(secret: string, recipientAddress: string, amount: bigint): Promise<string>`

Redeems a private transaction:

```typescript
// Recipient uses claiming key to withdraw
const txHash = await mistService.withdraw(claimingKey, recipientAddress, amount);
```

#### `fetchAssets(claimingKey: string, recipientAddress: string): Promise<MistAsset[]>`

Checks available assets from a private transaction:

```typescript
const assets = await mistService.fetchAssets(claimingKey, recipientAddress);
// Returns: [{ token: '0x...', amount: BigInt(...), decimals: 18 }]
```

#### `checkTransactionExists(claimingKey, recipient, token, amount): Promise<boolean>`

Verifies a transaction exists before claiming:

```typescript
const exists = await mistService.checkTransactionExists(
  claimingKey,
  recipientAddress,
  tokenAddress,
  amount
);
```

### 3. **Hook: useMistCash**

**Location**: `src/hooks/useMistCash.ts`

Provides context-aware MIST service:

```typescript
const {
  mistService,      // MistCashService instance
  isConnected,      // Boolean: wallet connected
  isReady,          // Boolean: wallet + MIST ready
  chamberAddress,   // Chamber contract address
  userAddress,      // Connected user address
  account,          // Starknet account instance
} = useMistCash();
```

### 4. **Dashboard Integration**

**Location**: `src/components/Dashboard.tsx`

The dashboard provides UI for:

- **Deposit Section**: 
  - Input STRK amount
  - Generates claiming key automatically
  - Shows claiming key for user to copy
  - Submits transaction

- **Withdraw Section**:
  - Input amount
  - Paste claiming key from recipient
  - Execute withdrawal

---

## Configuration

### Environment Variables

Add to your `.env.local`:

```bash
# MIST Chamber Contract Address
# Sepolia: Get from MIST team or @mistcash/config
# Mainnet: Get from MIST deployment
NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=0x...

# Starknet RPC (required for MIST service)
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_7/...

# Optional: Enable demo mode for testing
NEXT_PUBLIC_DEMO_MODE_ENABLED=true
```

### Finding Chamber Addresses

**Sepolia Testnet:**
1. Check MIST SDK documentation at https://docs.mistcash.com
2. Or ask MIST team in Discord
3. Contact: https://github.com/mistcash/sdk/issues

**Mainnet:**
1. Use production chamber address from MIST team
2. Update deployment configuration
3. Redeploy frontend with mainnet address

---

## Workflow: Private Deposit and Withdrawal

### Scenario: Alice sends STRK to Bob privately

#### Step 1: Alice Creates Private Deposit

```typescript
const { mistService } = useMistCash();

// Alice deposits 50 STRK for Bob
const amount = BigInt(50 * 1e18);
const claimingKey = 'mist_1733428800123_abc123xyz';
const txHash = await mistService.deposit(amount, bobAddress, claimingKey);

// ✅ Transaction is now on-chain but unlinkable to Alice
```

**Important**: No connection exists on-chain between Alice's wallet and this transaction.

#### Step 2: Alice Shares Claiming Key with Bob

Alice must **securely** share the claiming key with Bob:
- ✅ DO: Send via encrypted DM, secure channel
- ❌ DON'T: Post publicly, share insecurely

```
Claiming Key: mist_1733428800123_abc123xyz
Share this with the recipient only!
```

#### Step 3: Bob Verifies Transaction Exists (Optional)

Bob can verify the transaction was created:

```typescript
const exists = await mistService.checkTransactionExists(
  claimingKey,
  bobAddress,
  strkTokenAddress,
  amount
);

if (exists) {
  console.log('✅ Transaction found, safe to withdraw');
}
```

#### Step 4: Bob Withdraws to His Address

```typescript
const txHash = await mistService.withdraw(claimingKey, bobAddress, amount);

// ✅ Bob now receives 50 STRK with no on-chain link to Alice
```

---

## Privacy Properties

### What's Private?

✅ **Transaction sender** - Alice's address is not linked to the transaction
✅ **Transaction recipient** - Only Bob and Alice know Bob received funds
✅ **Amount** - Can be encrypted (optional)

### What's Public?

⚠️ **MIST Chamber** - The chamber contract address is visible
⚠️ **Token type** - STRK token address is on-chain
⚠️ **Timestamp** - Approximately when transaction was created

### Security Notes

⚠️ **No double-spend protection**: If Bob claims the same transaction twice, MIST cannot prevent it (claimed transactions remain claimable)
  - Solution: Backend must track claimed transactions
  - Obsqra: Transaction history in dashboard tracks claims

⚠️ **Claiming key security**: Treat claiming key like a password
  - If compromised, anyone can withdraw the funds
  - Use secure transmission channels

---

## Demo Mode vs Live Mode

### Demo Mode (Testing)

When `isDemoMode` is true in DemoModeContext:

```typescript
// Simulated MIST transaction
const mockTxHash = '0x' + randomHex();
const mockClaimingKey = 'claim_' + Date.now() + '_' + randomKey();

// UI shows success but no actual blockchain transaction
alert('🎮 Demo: Deposited 10 STRK via MIST.cash!');
```

**Use for:** Testing UI, workflow validation, demos

### Live Mode (Production)

When wallet is connected and `isDemoMode` is false:

```typescript
// Real MIST transaction on Starknet
const txHash = await mistService.deposit(amount, recipient, claimingKey);

// Transaction submitted to blockchain
// Must wait for confirmation (~6 seconds on Starknet)
```

**Use for:** Real deposits, actual fund transfers

---

## Error Handling

### Common Errors and Solutions

**Error**: "Account not connected"
```
Cause: User hasn't connected wallet
Solution: Show "Connect Wallet" button, connect before deposit
```

**Error**: "MIST.cash service not available"
```
Cause: Chamber address not configured in env
Solution: Set NEXT_PUBLIC_MIST_CHAMBER_ADDRESS in .env.local
```

**Error**: "Withdrawal failed: Transaction not found"
```
Cause: Invalid claiming key or transaction doesn't exist
Solution: Verify claiming key, check transaction was created
```

**Error**: "Insufficient balance"
```
Cause: Account doesn't have enough STRK
Solution: Fund account via faucet or transfer STRK
```

### Implementing Error Recovery

```typescript
try {
  const txHash = await mistService.deposit(amount, recipient, claimingKey);
  // Success: show confirmation
} catch (error) {
  if (error.message.includes('Account')) {
    // Handle: User not connected
  } else if (error.message.includes('balance')) {
    // Handle: Insufficient funds
  } else {
    // Handle: Other errors
  }
}
```

---

## Testing MIST Integration

### Prerequisites

1. Connected Starknet wallet (Argent X or Braavos)
2. Testnet STRK tokens (get from [faucet](https://starknet-faucet.vercel.app/))
3. Environment variables configured

### Test Procedure

1. **Start frontend in demo mode**:
   ```bash
   cd frontend
   npm install
   npm run dev
   # Visit http://localhost:3003
   ```

2. **Test demo deposits/withdrawals**:
   - Toggle Demo Mode in dashboard
   - Enter amount
   - Click "Deposit Privately"
   - Verify claiming key displayed
   - Check transaction in History tab

3. **Test live deposits** (requires testnet STRK):
   - Turn off Demo Mode
   - Connect wallet
   - Enter STRK amount
   - Click "Deposit Privately"
   - Check transaction on [Starkscan](https://sepolia.starkscan.co/)

4. **Test withdrawals**:
   - Copy claiming key from deposit
   - Go to Withdraw section
   - Paste claiming key
   - Click "Withdraw Privately"
   - Verify transaction submitted

### Verification Checklist

- [ ] Demo mode: Deposits/withdrawals work without wallet
- [ ] Live mode: Deposits create on-chain transactions
- [ ] Claiming keys: Generated and stored securely
- [ ] History: Transactions appear in History tab
- [ ] Error handling: Invalid keys show helpful errors
- [ ] Mobile: UI responsive on mobile devices

---

## Integration with Obsqra Strategy

MIST.cash enables Obsqra to offer:

1. **Privacy-preserving deposits** - Users' identities not linked to funds
2. **Compliant yield farming** - MIST provides regulatory flexibility
3. **Cross-protocol routing** - Funds routed through Nostra, zkLend, Ekubo privately
4. **DAO constraints** - Constraints apply to private transactions too

### Flow

```
User Deposit (Private)
    ↓ via MIST.cash
[Private STRK in MIST Chamber]
    ↓
StrategyRouter
    ↓
[Allocation: Nostra 40% / zkLend 30% / Ekubo 30%]
    ↓
[Yield generation across protocols]
    ↓ Withdraw request
[Claiming key + StrategyRouter]
    ↓
Private withdrawal back to user
```

---

## Mainnet Deployment

### Before Going to Mainnet

1. **Update Chamber Address**:
   ```bash
   # .env.local
   NEXT_PUBLIC_MIST_CHAMBER_ADDRESS=0x<mainnet-chamber-address>
   ```

2. **Update RPC Endpoint**:
   ```bash
   NEXT_PUBLIC_RPC_URL=https://starknet-mainnet.g.alchemy.com/starknet/version/rpc/v0_7/...
   ```

3. **Remove Demo Mode** (optional):
   ```bash
   NEXT_PUBLIC_DEMO_MODE_ENABLED=false
   ```

4. **Test thoroughly** on Sepolia before mainnet

### Getting Mainnet Chamber Address

Contact MIST team:
- GitHub: https://github.com/mistcash/sdk
- Email: Ask in Starknet community
- Documentation: https://docs.mistcash.com (coming soon)

---

## Troubleshooting

### MIST Service Initialization Fails

**Symptom**: "MIST service not initialized"

**Causes**:
1. Chamber address not set
2. RPC URL unreachable
3. Provider not initialized

**Solutions**:
```typescript
// Check in browser console
console.log('Chamber:', process.env.NEXT_PUBLIC_MIST_CHAMBER_ADDRESS);
console.log('RPC:', process.env.NEXT_PUBLIC_RPC_URL);
```

### Transactions Don't Appear in History

**Symptom**: Deposit submitted but not in History tab

**Causes**:
1. Transaction failed silently
2. History context not updated
3. LocalStorage cleared

**Solutions**:
```typescript
// Check browser console for errors
console.error('MIST deposit error:', error);

// Clear localStorage and try again
localStorage.clear();
```

### Withdrawal with Claiming Key Fails

**Symptom**: "Withdrawal failed: Transaction not found"

**Causes**:
1. Invalid claiming key format
2. Transaction already spent (claimed)
3. Key doesn't match recipient address

**Solutions**:
```typescript
// Verify key before withdrawing
const exists = await mistService.checkTransactionExists(
  claimingKey,
  recipientAddress,
  tokenAddress,
  amount
);

if (!exists) {
  // Check claiming key format and transaction details
}
```

---

## Resources

- **MIST.cash SDK**: https://github.com/mistcash/sdk
- **MIST NPM Packages**: https://www.npmjs.com/org/mistcash
- **Starknet Docs**: https://docs.starknet.io
- **Starknet React**: https://docs.starknet-react.com

---

## Next Steps

1. ✅ Set up environment variables with chamber address
2. ✅ Test deposits/withdrawals in demo mode
3. ✅ Connect wallet and test live mode
4. ✅ Verify transactions on Starkscan
5. ⏳ Deploy to mainnet with mainnet chamber address
6. ⏳ Monitor transaction volume and security

---

**Last Updated**: December 6, 2025  
**Status**: ✅ Integrated & Testable

