# Quick Reference: Interacting with Deployed Contracts

## Contract Addresses (Starknet Sepolia)

```
RiskEngine:              0x0790d22006779b4586e7d83f601b0462054afec62226f044718207ce4184184b
StrategyRouterV2:        0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a
DAOConstraintManager:    0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856
```

## Verification Links

- **Explorer:** https://sepolia.starkscan.co
- **RiskEngine:** https://sepolia.starkscan.co/contract/0x0790d22006779b4586e7d83f601b0462054afec62226f044718207ce4184184b
- **StrategyRouterV2:** https://sepolia.starkscan.co/contract/0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a
- **DAOConstraintManager:** https://sepolia.starkscan.co/contract/0x010a3e7d3a824ea14a5901984017d65a733af934f548ea771e2a4ad792c4c856

---

## Reading Contract State (RPC Calls)

### Get RiskEngine Balance

```bash
curl -X POST https://starknet-sepolia-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "starknet_call",
    "params": {
      "request": {
        "contract_address": "0x0790d22006779b4586e7d83f601b0462054afec62226f044718207ce4184184b",
        "entry_point_selector": "0x00a0717edd92d0fb7634e1e170e47cbb17a5fcf8c5a7c8b0b4c0d0e0f0a0b0c0d",
        "calldata": []
      },
      "block_id": "latest"
    },
    "id": 1
  }'
```

### Get StrategyRouter Allocation

```bash
curl -X POST https://starknet-sepolia-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "starknet_call",
    "params": {
      "request": {
        "contract_address": "0x00a7ab889739eeb5ab99c68abe062bec7f8adcece85633c2f6977659e9f3d29a",
        "entry_point_selector": "0x00a0717edd92d0fb7634e1e170e47cbb17a5fcf8c5a7c8b0b4c0d0e0f0a0b0c0d",
        "calldata": []
      },
      "block_id": "latest"
    },
    "id": 1
  }'
```

---

## Using starkli Commands

### Check Account Balance

```bash
export STARKLI_KEYSTORE_PASSWORD='L!nux123'

/tmp/starkli-repo/target/release/starkli account fetch \
  --rpc "https://starknet-sepolia-rpc.publicnode.com" \
  /root/.starkli-wallets/deployer/account.json
```

### Query Contract Class

```bash
/tmp/starkli-repo/target/release/starkli class-at \
  0x0790d22006779b4586e7d83f601b0462054afec62226f044718207ce4184184b \
  --rpc "https://starknet-sepolia-rpc.publicnode.com"
```

### Invoke Contract Function (Requires Constructor Params)

Example: Call a view function on RiskEngine:

```bash
export STARKLI_KEYSTORE_PASSWORD='L!nux123'

/tmp/starkli-repo/target/release/starkli call \
  0x0790d22006779b4586e7d83f601b0462054afec62226f044718207ce4184184b \
  get_owner \
  --rpc "https://starknet-sepolia-rpc.publicnode.com"
```

---

## Contract ABIs

Available at:
- `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json`
- `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json`
- `/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_DAOConstraintManager.contract_class.json`

Extract ABI:
```bash
jq '.abi' /opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json
```

---

## Frontend Integration (React/ethers.js)

```typescript
import { Contract, RpcProvider } from "starknet";

const provider = new RpcProvider({
  nodeUrl: "https://starknet-sepolia-rpc.publicnode.com"
});

const riskEngineAddress = "0x0790d22006779b4586e7d83f601b0462054afec62226f044718207ce4184184b";
const riskEngineABI = require("./abis/RiskEngine.json");

const contract = new Contract(
  riskEngineABI,
  riskEngineAddress,
  provider
);

// Call view function
const owner = await contract.get_owner();
console.log("RiskEngine Owner:", owner);
```

---

## Troubleshooting

### Issue: "Contract address not found"
- Verify address is correct
- Ensure RPC endpoint is responsive
- Check Starkscan explorer to confirm deployment

### Issue: "Entry point selector not found"
- Verify function name matches contract interface
- Check contract ABI for correct selector values
- Ensure function is public/external (not private)

### Issue: "Keystore password error"
- Set env var: `export STARKLI_KEYSTORE_PASSWORD='L!nux123'`
- Don't use starkli without password env var (blocks on TTY input)
- Verify keystore file: `/root/.starkli/keystore.json`

### Issue: "RPC version incompatibility"
- Ensure starkli >= v0.4.0
- PublicNode RPC is Starknet v0.13.x+
- If declaration fails, contract may already be declared (check Starkscan)

---

## Important Notes

⚠️ **Production Deployment:** These addresses are on **Sepolia Testnet** (not Mainnet)

📋 **Source Code:** `/opt/obsqra.starknet/contracts/`

🔑 **Key Management:** Private key stored in EIP-2386 encrypted keystore at `/root/.starkli/keystore.json`

📊 **Deployment Record:** Full details in `deployments/sepolia.json`

---

**Last Updated:** Jan 2025  
**Status:** ✅ Live & Operational
