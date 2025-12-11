# Lessons Learned: Building on Starknet

## 🎯 Project Overview
Obsqra.starknet - A verifiable AI infrastructure for private DeFi, combining Starknet smart contracts, MIST.cash privacy protocol, and AI-driven risk management.

---

## 📚 Latest: Strategy Router v3.5 Compilation & Deployment (December 10, 2025)

### Cairo Interface Dispatcher Pattern

**Challenge:** Using MIST Chamber interface defined in same file caused dispatcher access errors.

**Solution:** 
- Move interfaces to separate files (`interfaces/mist.cairo`)
- Import both `Dispatcher` and `DispatcherTrait`
- Pattern: `let chamber = IMistChamberDispatcher { contract_address: addr };`

**Key Insight:** Cairo auto-generates dispatcher types from `#[starknet::interface]` traits. You never declare them yourself - just import from the module where the interface lives.

### Tuple Destructuring in Cairo

**Challenge:** `read_tx()` returns `(ContractAddress, u256)` but destructuring failed.

**Solution:**
- Use: `let (token, amount) = dispatcher.read_tx(secret);`
- Cairo does NOT support `result.0` / `result.1` syntax
- If wrapped in `Result`, use `.unwrap()` first

### Doc Comments Parser Issues

**Challenge:** Compiler errors: "Expected a '!' after the identifier 'deposit' to start an inline macro"

**Root Cause:** Cairo's doc comment parser interprets certain words (like "deposit", "MIST", "transaction") as macro identifiers.

**Solution:** 
- Use regular comments (`//`) instead of doc comments (`/** */`) for these cases
- Or rephrase to avoid problematic words

**Example:**
```cairo
// ❌ This causes parser errors:
/**
 * Pattern 2: Commit to MIST deposit (Phase 1)
 */

// ✅ Use regular comments instead:
// Pattern 2: Commit phase - user sends hash of secret to router
```

### Map Access Pattern

**Challenge:** Direct `.read(key)` / `.write(key, value)` on storage maps causes errors.

**Solution:**
- Always use `.entry(key).read()` / `.entry(key).write(value)` for storage maps
- This is the Cairo 2.0+ pattern for `StorageMap` types

**Example:**
```cairo
// ❌ Old pattern (deprecated):
let balance = self.balances.read(user);

// ✅ New pattern (required):
let balance = self.balances.entry(user).read();
self.balances.entry(user).write(new_balance);
```

### Contract Fragmentation Problem

**Challenge:** Functions split across v2 and v3 contracts, frontend didn't know which to call.

**Solution:**
- Created unified v3.5 contract with all functions
- Frontend intelligently queries available functions (tries v3.5 first, falls back to v2)
- Maintains backward compatibility while providing unified interface

**Key Insight:** When adding features, consider backward compatibility. A unified contract is better than multiple versions, but if you must have versions, make the frontend smart enough to handle both.

---

## 🔥 Key Challenges & Solutions

### 1. **EVM → Starknet Migration**
**Challenge:** Initially built for EVM (Aave, Lido, Compound, ETH)  
**Solution:** Refactored to Starknet-native protocols (Nostra, zkLend, Ekubo) and STRK token

**Why it matters:** Starknet has its own DeFi ecosystem. Using native protocols ensures:
- Better integration with the network
- Lower gas costs
- Access to Starknet-specific features like account abstraction

---

### 2. **Account Deployment on Starknet**
**Challenge:** "Chicken and egg" problem - need account deployed to send transactions, but need to send transaction to deploy account

**How Starknet accounts work:**
1. Generate account address (deterministic from public key)
2. Fund the address with STRK (before deployment!)
3. First outgoing transaction triggers `DEPLOY_ACCOUNT`
4. Account contract gets deployed on-chain using pre-funded STRK

**Key insight:** Unlike EVM where addresses are just keypairs, Starknet accounts are actual smart contracts that need deployment.

---

### 3. **Tool Compatibility Hell**
**Challenge:** Different tools (`starkli`, `sncast`, `starknet-py`) had version mismatches with RPC endpoints

**What we learned:**
- `starkli 0.3.x` → expects RPC 0.7.0
- `sncast 0.39.x` → expects RPC 0.7.0  
- `sncast 0.53.0` → expects RPC 0.10.0
- Alchemy RPC → provides 0.8.1

**Solution:** Use `sncast --network sepolia` (built-in network configs handle compatibility automatically)

**Takeaway:** Always check compatibility tables: https://docs.starknet.io/learn/cheatsheets/compatibility

---

### 4. **CORS Issues with Public RPCs**
**Challenge:** Frontend couldn't connect to `starknet-sepolia.public.blastapi.io` due to CORS policy

**Root cause:** The `@starknet-react/chains` library's default `sepolia` config uses blastapi, which doesn't allow browser requests

**Solution:** Created custom chain config with Alchemy RPC:
```typescript
const sepoliaCustom: Chain = {
  id: BigInt('0x534e5f5345504f4c4941'),
  network: 'sepolia',
  // ... other config ...
  rpcUrls: {
    default: {
      http: ['https://starknet-sepolia.g.alchemy.com/v2/YOUR_KEY'],
    },
  },
};
```

**Takeaway:** Not all RPC providers support CORS for browser requests. Alchemy and Infura generally do.

---

### 5. **Testnet Faucet Rate Limits**
**Challenge:** Faucet (faucet.starknet.io) rate-limits by IP address

**Workarounds:**
- Connect GitHub account for higher limits
- Use mobile hotspot for fresh IP
- Alternative faucets: Alchemy, Blast, StarkGate

**Tip:** For development, keep one funded "deployer" account to transfer testnet tokens to other accounts

---

### 6. **Compiled Class Hash Mismatches**
**Challenge:** `starkli declare` failed with "Mismatch compiled class hash"

**Cause:** Compiler version mismatch between local Cairo compiler and what the RPC expects

**Solution:** 
- Ensure `scarb` version matches network requirements
- Recompile with `scarb build` after version updates
- Use `sncast` instead of `starkli` (better version handling)

---

### 7. **Transaction Nonce Issues**
**Challenge:** "Invalid transaction nonce" errors during rapid deployments

**Why:** Starknet transactions must have sequential nonces

**Solution:** Wait for previous transaction confirmation before sending next one

**Code pattern:**
```typescript
const result = await account.execute([{ ... }]);
await account.waitForTransaction(result.transaction_hash); // ← Critical!
```

---

## 🎓 Starknet-Specific Learnings

### Account Abstraction is Real
- Every account is a smart contract
- Accounts must be deployed with `DEPLOY_ACCOUNT` transaction
- You can customize account logic (multisig, session keys, etc.)

### STRK for Gas
- STRK (not ETH) is the native gas token
- Fee estimation is different from EVM
- V3 transactions require resource bounds (`l1_gas`, `l2_gas`)

### Cairo is Not Solidity
- Immutable by default
- Explicit storage access
- Different testing patterns
- Felt252 is the primitive type

### Block Explorer Delays
- Voyager/Starkscan may lag behind actual chain state
- Direct RPC queries are more reliable for recent transactions
- Use `starknet_getTransactionReceipt` for confirmation

---

## 🛠️ Recommended Development Stack

### Deployment
- **sncast** (Starknet Foundry) - Best for contract deployment
- **scarb** - Cairo project management and compilation

### Frontend
- **@starknet-react/core** - React hooks for Starknet
- **starknet.js** - Core Starknet JavaScript library
- **Next.js** - Frontend framework

### Backend/AI Service
- **starknet-py** - Python library for Starknet interaction
- **FastAPI** - API framework

### RPCs
- **Alchemy** - Best CORS support for browsers
- **Infura** - Reliable alternative
- **Public nodes** - Use only for read operations

---

## 📈 Development Workflow That Works

1. **Local Development**
   - Use Starknet devnet for rapid iteration
   - Mock contract interactions in frontend

2. **Testnet Deployment** (Sepolia)
   - Get STRK from faucet FIRST
   - Use `sncast` with `--network sepolia`
   - Verify on Voyager/Starkscan
   - Test frontend integration

3. **Mainnet Preparation**
   - Audit smart contracts
   - Test with real STRK (small amounts)
   - Monitor gas costs
   - Have contingency plan for upgrades

---

## 🚨 Common Pitfalls to Avoid

1. ❌ **Don't** hardcode RPC URLs without CORS support in frontend
2. ❌ **Don't** try to deploy account without funding it first
3. ❌ **Don't** use `starkli` and `sncast` interchangeably (different config formats)
4. ❌ **Don't** send transactions without waiting for confirmation
5. ❌ **Don't** assume EVM patterns work on Starknet
6. ❌ **Don't** rely solely on block explorers for recent transactions

✅ **DO** check tool compatibility with network RPC version  
✅ **DO** use official faucets and be patient with rate limits  
✅ **DO** read Starknet docs thoroughly (very different from EVM)  
✅ **DO** test account deployment flow early in development  
✅ **DO** handle errors gracefully (Starknet errors can be cryptic)

---

## 🎯 Final Thoughts

**Building on Starknet requires a mindset shift from EVM.**

- **Good:** Account abstraction, Cairo safety, proving system
- **Challenging:** Tooling maturity, different paradigms, steeper learning curve
- **Worth it:** Scalability, lower costs, innovation opportunities

**The ecosystem is evolving rapidly** - expect frequent breaking changes in tooling and libraries. Pin your dependencies and check release notes regularly.

---

## 📚 Essential Resources

- Official Docs: https://docs.starknet.io
- Cairo Book: https://book.cairo-lang.org
- Starknet Foundry: https://foundry-rs.github.io/starknet-foundry
- Starknet React: https://starknet-react.com
- Community: https://community.starknet.io

---

**Built with caffine and stress (and a lot of debugging) by the Obsqra team**

