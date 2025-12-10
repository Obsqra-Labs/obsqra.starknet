# Deploy StrategyRouterV2 with ETH as Asset Token

## ✅ What's Fixed

**Contract Updated:**
- ✅ `deposit()` now accepts **ETH** (not STRK)
- ✅ Swaps half ETH → STRK for pools
- ✅ Deploys to JediSwap + Ekubo with both tokens

**Deployment Script Created:**
- ✅ `deploy-v2-eth.sh` - Ready to use
- ✅ Uses `sncast --network sepolia` (handles RPC compatibility)
- ✅ Uses ETH as `asset_token` in constructor
- ✅ Uses real protocol addresses from `protocol_addresses_sepolia.json`

---

## 🚀 How to Deploy

### Prerequisites

1. **Deployer account funded with STRK** (for gas):
   ```bash
   # Check balance
   sncast --account deployer --network sepolia account balance
   
   # If 0, get from faucet:
   # https://starknet-faucet.vercel.app/
   ```

2. **Account configured in Scarb.toml:**
   ```toml
   [tool.sncast.deployer]
   account = "deployer"
   accounts-file = "~/.starknet_accounts/starknet_open_zeppelin_accounts.json"
   network = "alpha-sepolia"
   ```

### Deploy

```bash
cd /opt/obsqra.starknet
./deploy-v2-eth.sh
```

**What it does:**
1. ✅ Checks deployer balance
2. ✅ Builds contracts (`scarb build`)
3. ✅ Declares StrategyRouterV2
4. ✅ Deploys with ETH as `asset_token`
5. ✅ Saves deployment info
6. ✅ Updates frontend `.env.local`

---

## 📋 Constructor Parameters

The script deploys with:

| Parameter | Address | Description |
|-----------|---------|-------------|
| `owner` | `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d` | Deployer wallet |
| `jediswap_router` | `0x03c8e56d7f6afccb775160f1ae3b69e3db31b443e544e56bd845d8b3b3a87a21` | JediSwap Swap Router |
| `jediswap_nft_manager` | `0x024fd9721eea36cf8cebc226fd9414057bbf895b47739822f849f622029f9399` | JediSwap V2 NFT Position Manager |
| `ekubo_core` | `0x0444a09d96389aa7148f1aada508e30b71299ffe650d9c97fdaae38cb9a23384` | Ekubo Core |
| `risk_engine` | `0x008c3eff435e859e3b8e5cb12f837f4dfa77af25c473fb43067adf9f557a3d80` | Risk Engine |
| `dao_manager` | `0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856` | DAO Constraint Manager |
| `asset_token` | `0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7` | **ETH** ✅ |

---

## 🔍 Verify Deployment

After deployment, verify:

```bash
# Check allocation (should be 50/50)
sncast --account deployer --network sepolia call \
  --contract-address <DEPLOYED_ADDRESS> \
  --function get_allocation

# Check asset token (should be ETH address)
sncast --account deployer --network sepolia call \
  --contract-address <DEPLOYED_ADDRESS> \
  --function get_asset_token
```

---

## 🎯 Testing

Once deployed:

1. **Deposit ETH:**
   - User deposits ETH (not STRK!)
   - Contract swaps half ETH → STRK
   - Adds liquidity to both protocols

2. **Check positions:**
   - JediSwap: NFT position IDs stored
   - Ekubo: Position IDs stored

3. **Verify on Starkscan:**
   - Check contract address
   - View transaction history
   - Verify constructor parameters

---

## 📝 Lessons Learned Applied

✅ **RPC Compatibility:**
- Uses `sncast --network sepolia` (handles version automatically)
- No need to worry about RPC 0.7.1 vs 0.10.0

✅ **Account Setup:**
- Checks balance before deploying
- Uses profile from `Scarb.toml`

✅ **Build First:**
- Runs `scarb build` before declaring
- Ensures latest code is compiled

✅ **Real Addresses:**
- Uses addresses from `protocol_addresses_sepolia.json`
- No placeholders

✅ **ETH as Asset:**
- Correct token for user deposits
- Matches what users actually have

---

## 🐛 Troubleshooting

### "Account not found"
```bash
# Make sure account is imported
sncast account import \
  --name deployer \
  --address <YOUR_ADDRESS> \
  --private-key <YOUR_KEY> \
  --type oz
```

### "Insufficient balance"
Get STRK from faucet: https://starknet-faucet.vercel.app/

### "Class already declared"
Delete `/opt/obsqra.starknet/deployments/v2_eth_class_hash.txt` to redeclare

### "Build failed"
```bash
cd /opt/obsqra.starknet/contracts
scarb build
# Check for compilation errors
```

---

## 📚 References

- **Lessons Learned:** `/opt/obsqra.starknet/docs/LESSONS_LEARNED.md`
- **Protocol Addresses:** `/opt/obsqra.starknet/contracts/protocol_addresses_sepolia.json`
- **Contract Code:** `/opt/obsqra.starknet/contracts/src/strategy_router_v2.cairo`
- **Previous Deployment:** `/opt/obsqra.starknet/STRATEGYROUTER_V2_DEPLOYMENT.md`

---

**Ready to deploy!** 🚀

Run: `./deploy-v2-eth.sh`


