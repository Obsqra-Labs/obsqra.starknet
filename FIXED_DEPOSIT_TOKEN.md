# Fixed: Contract Now Accepts ETH (Not STRK) ✅

## The Fix

**You were absolutely right!** We had it backwards.

**Before (Wrong):**
- Contract expected STRK deposits
- Swapped STRK → ETH
- But users have ETH, not STRK!

**After (Fixed):**
- Contract now expects **ETH deposits** ✅
- Swaps ETH → STRK (half)
- Adds liquidity with both ETH + STRK
- Makes way more sense!

---

## What Changed

### Updated deposit() Function:

**Now:**
1. User deposits **ETH** ✅
2. Contract swaps **half ETH → STRK**
3. Adds liquidity with **ETH + STRK** to both protocols
4. Stores position IDs

**Token Logic:**
- **Primary deposit token**: ETH (what users have)
- **Gas token**: STRK (for transactions)
- **Pool tokens**: ETH + STRK (both needed)

---

## Updated Flow

```
User deposits 1 ETH
    ↓
Contract receives 1 ETH
    ↓
Allocation: 50% JediSwap, 50% Ekubo
    ↓
JediSwap (0.5 ETH):
  - Swap 0.25 ETH → STRK
  - Add liquidity: 0.25 ETH + STRK received
    ↓
Ekubo (0.5 ETH):
  - Swap 0.25 ETH → STRK
  - Deposit: 0.25 ETH + STRK received
    ↓
Positions created ✅
Funds earning yield ✅
```

---

## Important Notes

### Token Order Matters!

For JediSwap pools, tokens are ordered by address:
- **STRK**: `0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f36c338bb1`
- **ETH**: `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7`

STRK < ETH (lexicographically), so:
- **token0** = STRK
- **token1** = ETH

The code now handles this correctly!

---

## Deployment Update Needed

**When deploying, set `asset_token` to ETH address:**

```cairo
constructor(
    owner: ...,
    jediswap_router: ...,
    jediswap_nft_manager: 0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399,
    ekubo_core: 0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384,
    risk_engine: ...,
    dao_manager: ...,
    asset_token: 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7  // ETH!
)
```

---

## Testing

Now you can:
1. **Deposit ETH directly** ✅
2. Contract swaps half to STRK
3. Adds liquidity to both protocols
4. Funds start earning yield!

**No need to swap ETH → STRK first!**

---

## About Yield

**Are we earning yield now?**

**If deposit() succeeds:**
- ✅ Funds are deployed to protocols
- ✅ They're earning yield in the background
- ❌ But we still can't see it (accrue_yields() returns 0)
- ⏳ Need to implement position value queries

**The decimals you see:**
- Still likely **gas fees** (STRK spent)
- Or **rounding** in display
- **Not visible yield** (because we're not tracking it yet)

---

## Next Steps

1. **Redeploy contract** with ETH as asset_token
2. **Test deposit** with your ETH
3. **Verify** positions are created
4. **Implement yield tracking** so we can see actual returns

Good catch on the token logic! 🎯


