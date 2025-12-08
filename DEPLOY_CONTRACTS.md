#  Deploy Contracts to Sepolia

**Account:** 0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd

---

## Step 1: Deploy RiskEngine

```bash
cd /opt/obsqra.starknet/contracts

# Declare the contract
starkli declare \
  target/dev/obsqra_contracts_RiskEngine.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 Copy the CLASS_HASH from the output above!**

Then deploy:

```bash
# Replace <CLASS_HASH> with the actual hash from above
starkli deploy \
  <CLASS_HASH> \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 Save this CONTRACT_ADDRESS → This is your RiskEngine address!**

---

## Step 2: Deploy StrategyRouter

```bash
# Declare
starkli declare \
  target/dev/obsqra_contracts_StrategyRouter.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Deploy (replace <CLASS_HASH> from output above)
starkli deploy \
  <CLASS_HASH> \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 Save this CONTRACT_ADDRESS → This is your StrategyRouter address!**

---

## Step 3: Deploy DAOConstraintManager

```bash
# Declare
starkli declare \
  target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json

# Deploy (replace <CLASS_HASH> from output above)
starkli deploy \
  <CLASS_HASH> \
  0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd \
  --rpc https://starknet-sepolia.public.blastapi.io/rpc/v0_7 \
  --account ~/.starkli-wallets/deployer/account.json \
  --keystore ~/.starkli-wallets/deployer/keystore.json
```

**📝 Save this CONTRACT_ADDRESS → This is your DAOConstraintManager address!**

---

## Step 4: Track Your Addresses

Save all 3 addresses here as you deploy them:

```
RiskEngine:           0x_______________
StrategyRouter:       0x_______________
DAOConstraintManager: 0x_______________
```

---

## Next: Update Frontend

Once all 3 are deployed, update `/opt/obsqra.starknet/frontend/.env.local` with the addresses!
