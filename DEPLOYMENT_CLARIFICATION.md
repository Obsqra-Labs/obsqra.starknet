# FactRegistry Deployment - Important Clarification

## Option 1 vs Option 2 - The Real Difference

### Option 1: Use Existing Contract (Herodotus's Deployment)
- **Address**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`
- **Cost**: **Just gas fees** (~$0.01-0.10 per proof)
- **Credits needed**: **NO** ❌
- **API keys needed**: **NO** ❌
- **Setup**: Just use the address

### Option 2: Deploy Your Own
- **Cost**: Deployment gas (~$1-5) + gas per proof
- **Credits needed**: **NO** ❌
- **API keys needed**: **NO** ❌
- **Setup**: Deploy contract yourself

## The Confusion: Credits vs Gas

**Credits** are only needed for:
- Herodotus **Atlantic** (proof generation service)
- But you have **LuminAIR**, so you don't need Atlantic!

**Gas fees** are needed for:
- Calling any contract (including existing FactRegistry)
- Deploying your own contract
- This is normal blockchain usage

## Recommendation

**Use Option 1** - it's:
- ✅ Already deployed (no setup)
- ✅ Just gas fees (no credits)
- ✅ Standard practice
- ✅ Works immediately

Your code already uses this address in `backend/app/services/integrity_service.py`:
```python
INTEGRITY_VERIFIER_SEPOLIA = 0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c
```

## If You Still Want Option 2

The RPC version issue is blocking deployment. Options:
1. Wait for RPC compatibility fix
2. Use a different RPC endpoint (compatible with sncast 0.10.0)
3. Use starkli with proper keystore setup
4. Deploy manually via Starknet explorer

But honestly, **Option 1 is the way to go** - everyone uses it!
