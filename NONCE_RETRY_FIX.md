# Nonce Retry Logic Fix

**Date**: 2026-01-27  
**Status**: Nonce retry logic added, testing in progress

---

## 🎯 Issue: Invalid Transaction Nonce

**Error**: `Invalid transaction nonce`

**Root Causes**:
1. Concurrent transactions using same backend account
2. RPC lag between pending/latest nonce
3. Starknet_py nonce cache not aligned in async retries

---

## ✅ Fix Applied

### 1. Nonce Resync Retry Logic

**In `integrity_service.py`**:
- Fetches both `pending` and `latest` nonce
- Uses `max(pending, latest)` to avoid mismatch
- On nonce error, re-fetches latest and retries once
- Prevents infinite retry loops (max 1 retry)

### 2. Structured Logging

**Logs**:
- `pending_nonce`: Nonce from pending block
- `latest_nonce`: Nonce from latest block
- `used_nonce`: Nonce actually used (max of pending/latest)
- `rpc`: RPC URL used
- `attempt`: Retry attempt number

**Example log**:
```
Integrity invoke nonce state (attempt 1): pending_nonce=5, latest_nonce=6, used_nonce=6, rpc=https://...
```

---

## 🔍 How It Works

### Nonce Selection Strategy

```python
# Fetch both nonces
pending_nonce = await account.get_nonce(block_number="pending")
latest_nonce = await account.get_nonce(block_number="latest")

# Use the higher one to avoid mismatch
nonce = max(pending_nonce, latest_nonce)
```

**Why**: If pending has a lower nonce (tx not yet included), using latest prevents mismatch.

### Retry Logic

```python
try:
    invoke = await account.execute_v3(..., nonce=nonce, ...)
except Exception as e:
    if "nonce" in error_str and retry_count == 0:
        # Re-fetch latest nonce and retry once
        latest_nonce_retry = await account.get_nonce(block_number="latest")
        return await _invoke(client, rpc_url, retry_count=1)
```

**Why**: Nonce errors are often transient (RPC lag). One retry with fresh nonce usually fixes it.

---

## 📊 Expected Behavior

### Before (Broken)

```
Get nonce: pending=5, latest=6
Use nonce: 5
  ↓
Error: Invalid transaction nonce ❌
```

### After (Fixed)

```
Get nonce: pending=5, latest=6
Use nonce: 6 (max)
  ↓
Success: Transaction accepted ✅
```

**Or if nonce error occurs**:

```
Get nonce: pending=5, latest=6
Use nonce: 6
  ↓
Error: Invalid transaction nonce
  ↓
Re-fetch: latest=7
Retry with: 7
  ↓
Success: Transaction accepted ✅
```

---

## 🎯 Next Steps

### Testing

1. ✅ Nonce retry logic added
2. ✅ Structured logging added
3. ⏳ Test proof generation
4. ⏳ Check nonce logs
5. ⏳ Verify proof verification (if nonce fixed)

### Verification

After nonce is fixed, we'll see:
- ✅ Proof layout: recursive
- ✅ Proof segments: bitwise, no ecdsa
- ✅ Nonce: Synced correctly
- ⏳ Integrity verification result (OODS / final_pc / success)

---

## 🎓 Key Insights

### What We Learned

1. **Layout fixed ≠ Verification guaranteed**
   - Layout mismatch is fixed ✅
   - But OODS can still fail for AIR/params/serialization reasons
   - Need to test actual verification

2. **Nonce errors are separate**
   - Not related to proof validity
   - Pure account state management
   - Retry logic helps with RPC lag

3. **Structured logging is critical**
   - Helps debug nonce drift
   - Shows which RPC is used
   - Tracks retry attempts

---

**Status**: Nonce retry logic added. Testing to see if nonce issue is resolved and what the actual verification error is (if any).
