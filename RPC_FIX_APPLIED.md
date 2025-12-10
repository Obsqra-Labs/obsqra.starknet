# RPC Endpoint Fix Applied

## Problem

**Error:** `POST https://free-rpc.nethermind.io/sepolia-juno net::ERR_NAME_NOT_RESOLVED`

**Root Cause:**
- The `@starknet-react/core` library's default `sepolia` chain was using Nethermind RPC
- Nethermind RPC endpoint is not resolving (DNS failure or endpoint down)
- This caused all RPC calls to fail

## Fix Applied

### 1. Updated StarknetProvider
**File:** `/opt/obsqra.starknet/frontend/src/providers/StarknetProvider.tsx`

**Changes:**
- Created custom `sepoliaCustom` chain with explicit Alchemy RPC URL
- Replaced default `sepolia` chain with `sepoliaCustom`
- Ensures all account operations use reliable Alchemy RPC

**Before:**
```typescript
const chains = [sepolia]; // Uses default Nethermind RPC
```

**After:**
```typescript
const sepoliaCustom: Chain = {
  ...sepolia,
  rpcUrls: {
    default: {
      http: ['https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7'],
    },
  },
};
const chains = [sepoliaCustom]; // Uses reliable Alchemy RPC
```

### 2. Updated Config Defaults
**File:** `/opt/obsqra.starknet/frontend/src/lib/config.ts`

**Changes:**
- Changed default RPC from `publicnode.com` to Alchemy
- Alchemy is more reliable and has better CORS support

**Before:**
```typescript
const rpcUrl = process.env.NEXT_PUBLIC_RPC_URL || 'https://starknet-sepolia-rpc.publicnode.com';
```

**After:**
```typescript
const rpcUrl = process.env.NEXT_PUBLIC_RPC_URL || 
               'https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7';
```

## Why This Fixes It

1. **Account Provider**: The account from `@starknet-react/core` uses the chain's RPC URL
2. **Custom Chain**: By creating a custom chain with explicit Alchemy RPC, all account operations use Alchemy
3. **Contract Calls**: `useStrategyDeposit` already uses `config.rpcUrl` which now defaults to Alchemy
4. **Consistency**: All RPC calls now use the same reliable endpoint

## Testing

After this fix:
1. **Refresh the page** (or rebuild frontend)
2. **Try deposit again**
3. Should now use Alchemy RPC instead of Nethermind
4. RPC calls should succeed

## RPC Endpoints Used

**Primary:** Alchemy (`https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7`)
- ✅ Most reliable
- ✅ Good CORS support
- ✅ Fast response times

**Fallback:** PublicNode (`https://starknet-sepolia-rpc.publicnode.com`)
- ✅ Free
- ⚠️ Can be slower
- ⚠️ Sometimes has CORS issues

**Avoid:** Nethermind (`https://free-rpc.nethermind.io/sepolia-juno`)
- ❌ Not resolving (DNS failure)
- ❌ Unreliable

## Environment Variables

If you want to override the RPC, set in `.env.local`:

```bash
NEXT_PUBLIC_RPC_URL=https://starknet-sepolia.g.alchemy.com/v2/YOUR_KEY
```

Or use the proxy (for production):
```bash
# Uses /api/rpc proxy (which forwards to Alchemy)
# Automatically used when served over HTTPS
```

---

**Fix applied!** The frontend should now use reliable Alchemy RPC for all operations. 🚀


