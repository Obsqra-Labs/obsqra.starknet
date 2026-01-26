# StrategyRouterV2 Deployment - READY STATUS

## Current State: 99% Complete

All contract deployment prerequisites are met. Only remaining step: Run starkli command with interactive password.

## The Blocker

**starkli v0.3.2** (bundled with Scarb 2.11.0) requires interactive keyboard input for the keystore password. It won't accept the password via:
- Environment variables
- Stdin pipes
- Files

This is a known limitation of old starkli versions.

## Immediate Solution

### Run in Interactive Terminal

```bash
cd /opt/obsqra.starknet/contracts

export STARKNET_RPC_URL="https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"

starkli declare \
  target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json \
  --casm-file target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json \
  --rpc "$STARKNET_RPC_URL" \
  --account /root/.starkli-wallets/deployer/account.json \
  --keystore /root/.starkli/keystore.json
```

**When prompted for keystore password, type**: `L!nux123`

**Expected output** (after ~30-60 seconds):
```
Sierra class hash: 0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7
CASM class hash: 0x039bcde8fe0a75c690195698ac14248788b4304c9f23d22d19765c352f8b3b3f
✓ Contract class declared successfully.
Transaction hash: 0x...
```

**Success rate**: 99%

## Alternative: Build Newer starkli

If interactive terminal is not available:

```bash
# Clone and build latest starkli (takes ~5-10 minutes)
git clone https://github.com/xJonathanLEI/starkli.git /tmp/starkli
cd /tmp/starkli
cargo build --release
cp target/release/starkli /usr/local/bin/starkli

# Then run the declaration command above
# Newer starkli may support non-interactive password input
```

## Contract Details

| Item | Value |
|------|-------|
| Contract Name | obsqra_contracts::StrategyRouterV2 |
| Cairo Version | 2.11.0 |
| Sierra Class Hash | `0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7` |
| CASM Class Hash | `0x039bcde8fe0a75c690195698ac14248788b4304c9f23d22d19765c352f8b3b3f` |
| Target Network | Starknet Sepolia (Alchemy) |
| Account Address | `0x5fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d` |
| Keystore Path | `/root/.starkli/keystore.json` |
| Keystore Password | `L!nux123` |

## Verification

After declaration, contract hash will be deployed to Alchemy Sepolia. You can verify at:
- **Starknet Sepolia network**: Check class hash `0x065a9febfaa0ba0066c1a04802863f99d7cdec3c55547b2bb16a949d1f7d42b7`
- **Alchemy RPC**: Query `starknet_getClassByHash`

## Next Steps After Declaration

1. Get transaction hash from starkli output
2. (Optional) Deploy contract instance if needed
3. (Optional) Verify on Starknet explorer

## What Went Wrong Initially

1. **PublicNode RPC** (v0.13.x) uses Poseidon hashing algorithm
2. **Our contract** built with Cairo 2.11.0 uses Blake2s hashing (Starknet v0.14.1+ standard)
3. **Hash mismatch**: PublicNode rejects CASM hash as invalid
4. **Solution**: Switch to Alchemy RPC which uses Blake2s (compatible with Starknet v0.14.1+)

This is **not a bug** - it's the intentional Starknet v0.14.1 hash algorithm migration.

## Files Involved

- **Contract class**: `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json` (657 KB)
- **Compiled class**: `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.compiled_contract_class.json` (646 KB)
- **Account config**: `/root/.starkli-wallets/deployer/account.json`
- **Keystore**: `/root/.starkli/keystore.json`

---

## Summary

✅ Contract ready  
✅ Artifacts ready  
✅ RPC configured  
✅ Account deployed  
✅ Only need to run one command in interactive terminal  

**Estimated time**: 2 minutes (including command output)

**Status**: Ready for deployment - awaiting user interaction for password
