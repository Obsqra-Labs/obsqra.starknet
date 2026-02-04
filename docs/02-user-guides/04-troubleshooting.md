# Troubleshooting

This guide covers common issues, solutions, and frequently asked questions.

## Common Issues and Solutions

### Proof Generation Failures

#### Issue: Proof Generation Times Out

**Symptoms:**
- "Generating proof..." message persists
- No proof hash appears
- Request times out after 30+ seconds

**Possible Causes:**
1. Stone prover service unavailable
2. Resource constraints (CPU/memory)
3. Network connectivity issues
4. Trace generation errors

**Solutions:**

1. **Check Prover Service:**
   ```bash
   # Verify Stone prover is available
   which cpu_air_prover
   # Or check if service is running
   ps aux | grep stone
   ```

2. **Check Backend Logs:**
   ```bash
   # View backend logs
   tail -f /opt/obsqra.starknet/backend/logs/app.log
   # Look for prover errors
   ```

3. **Restart Services:**
   ```bash
   # Restart backend
   systemctl restart obsqra-backend
   # Or manually
   cd /opt/obsqra.starknet/backend
   python3 main.py
   ```

4. **Fallback to LuminAIR:**
   - If Stone prover unavailable
   - System should auto-fallback
   - Check configuration

#### Issue: Proof Generation Fails with Error

**Symptoms:**
- Error message displayed
- Proof generation fails immediately
- Specific error code shown

**Common Errors:**

**Error: "Trace generation failed"**
- **Cause:** Cairo execution error
- **Solution:** Check input metrics validity
- **Fix:** Verify protocol metrics are correct

**Error: "FRI parameters invalid"**
- **Cause:** Dynamic FRI calculation error
- **Solution:** Check trace size
- **Fix:** System should auto-calculate, check logs

**Error: "Prover binary not found"**
- **Cause:** Stone prover not installed
- **Solution:** Install Stone prover
- **Fix:** Follow installation guide

### Verification Delays

#### Issue: Verification Status Stuck on "Pending"

**Symptoms:**
- Status shows "Pending" for extended time
- No verification confirmation
- Fact hash not appearing

**Possible Causes:**
1. Fact Registry network issues
2. Integrity service unavailable
3. Network connectivity problems
4. Backend service errors

**Solutions:**

1. **Check Fact Registry:**
   ```bash
   # Query Fact Registry directly
   curl -X POST https://starknet-sepolia-rpc.publicnode.com \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "starknet_call",
       "params": {
         "contract_address": "0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64",
         "entry_point_selector": "get_all_verifications_for_fact_hash",
         "calldata": ["0x..."]
       }
     }'
   ```

2. **Check Integrity Service:**
   ```bash
   # Verify service is running
   curl https://atlantic.api.herodotus.cloud/health
   # Check API key is valid
   ```

3. **Check Backend Logs:**
   ```bash
   # Look for verification errors
   grep "verification" /opt/obsqra.starknet/backend/logs/app.log
   ```

4. **Retry Verification:**
   - Wait 1-2 minutes
   - Check status again
   - If still pending, contact support

#### Issue: Verification Fails

**Symptoms:**
- Status shows "Failed"
- Error message displayed
- Proof cannot be used

**Possible Causes:**
1. Invalid proof format
2. Fact Registry rejection
3. Network errors
4. Service configuration issues

**Solutions:**

1. **Check Proof Validity:**
   - Verify proof was generated correctly
   - Check proof size and format
   - Review generation logs

2. **Check Fact Registry:**
   - Verify registry is operational
   - Check network connectivity
   - Review registry logs

3. **Retry Generation:**
   - Generate new proof
   - Verify inputs are correct
   - Check for system updates

### Transaction Failures

#### Issue: Transaction Reverts

**Symptoms:**
- Transaction submitted but reverts
- Error message in transaction
- Allocation not executed

**Common Revert Reasons:**

**"Proof not verified"**
- **Cause:** Proof not in Fact Registry
- **Solution:** Wait for verification
- **Fix:** Ensure proof is verified before execution

**"Risk score mismatch"**
- **Cause:** On-chain calculation doesn't match proof
- **Solution:** Check metrics are correct
- **Fix:** Verify input data

**"Constraints violated"**
- **Cause:** Allocation violates DAO constraints
- **Solution:** Review constraint settings
- **Fix:** Adjust allocation or constraints

**"Insufficient balance"**
- **Cause:** Not enough funds for allocation
- **Solution:** Check wallet balance
- **Fix:** Deposit more funds

**Solutions:**

1. **Check Transaction Details:**
   ```bash
   # View transaction on Starkscan
   # https://sepolia.starkscan.co/tx/{tx_hash}
   ```

2. **Review Error Message:**
   - Read revert reason
   - Check contract state
   - Verify inputs

3. **Verify Preconditions:**
   - Proof is verified
   - Metrics are valid
   - Constraints are satisfied
   - Balance is sufficient

#### Issue: Transaction Stuck

**Symptoms:**
- Transaction submitted but not confirming
- Status shows "Pending" for extended time
- No block confirmation

**Possible Causes:**
1. Network congestion
2. Low gas fee
3. RPC issues
4. Transaction dropped

**Solutions:**

1. **Check Network Status:**
   ```bash
   # Check Starknet Sepolia status
   curl https://starknet-sepolia-rpc.publicnode.com
   ```

2. **Increase Gas Fee:**
   - Resubmit with higher fee
   - Check current gas prices
   - Adjust fee settings

3. **Check Transaction Status:**
   ```bash
   # Query transaction
   curl -X POST https://starknet-sepolia-rpc.publicnode.com \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "starknet_getTransactionStatus",
       "params": {"transaction_hash": "0x..."}
     }'
   ```

4. **Resubmit if Needed:**
   - If transaction dropped
   - Generate new proof
   - Submit new transaction

### Wallet Connection Issues

#### Issue: Wallet Won't Connect

**Symptoms:**
- "Connect Wallet" button doesn't work
- Wallet popup doesn't appear
- Connection fails

**Solutions:**

1. **Check Wallet Extension:**
   - Ensure extension is installed
   - Check extension is enabled
   - Verify extension is unlocked

2. **Check Network:**
   - Wallet must be on Sepolia
   - Verify network settings
   - Switch network if needed

3. **Clear Browser Cache:**
   - Clear cache and cookies
   - Refresh page
   - Try again

4. **Try Different Wallet:**
   - Try Argent X if using Braavos
   - Try Braavos if using Argent X
   - Check wallet compatibility

#### Issue: Transaction Signing Fails

**Symptoms:**
- Transaction popup appears
- Signing fails or is rejected
- Error message shown

**Solutions:**

1. **Check Wallet Balance:**
   - Ensure sufficient STRK for gas
   - Minimum: 0.01 STRK
   - Recommended: 0.1 STRK

2. **Check Transaction Details:**
   - Review transaction parameters
   - Verify contract addresses
   - Check gas estimates

3. **Approve Transaction:**
   - Click "Approve" in wallet
   - Wait for confirmation
   - Check for errors

## FAQ

### General Questions

**Q: What is a STARK proof?**
A: A STARK proof is a cryptographic proof that a computation was executed correctly. It can be verified by anyone without revealing the computation details.

**Q: How long does proof generation take?**
A: Typically 2-4 seconds using the Stone prover. LuminAIR may take slightly longer.

**Q: How much does it cost?**
A: Proof generation is free (local Stone prover). Transaction fees are $0.001-0.01 STRK on Starknet.

**Q: Can I verify proofs independently?**
A: Yes! Download the proof and use a STARK verifier tool. All proofs are publicly verifiable.

### Technical Questions

**Q: What happens if proof generation fails?**
A: The system will retry automatically. If it continues to fail, check backend logs and prover service status.

**Q: How do I know if my proof is verified?**
A: Check the verification status in the UI or via API. Status will show "Verified" when confirmed.

**Q: What is the Fact Registry?**
A: The Fact Registry (SHARP) is an on-chain contract that stores verified computation facts. It enables on-chain proof verification.

**Q: Can I use my own Fact Registry?**
A: Yes, you can deploy your own Fact Registry. See the deployment guide for details.

### Allocation Questions

**Q: How are allocations calculated?**
A: Allocations are calculated based on risk-adjusted APY, respecting DAO constraints. The formula is: `Allocation = (APY * 10000) / (Risk + 1)`.

**Q: What are DAO constraints?**
A: DAO constraints are governance parameters like maximum single protocol allocation, minimum diversification, etc.

**Q: Can I override allocations?**
A: No, allocations are calculated deterministically and verified on-chain. DAO can update constraints through governance.

**Q: How often are allocations updated?**
A: Allocations are updated when you trigger a new allocation. There's no automatic rebalancing (yet).

### Model Questions

**Q: How do model upgrades work?**
A: Model upgrades are managed through the ModelRegistry contract. Only the owner can register new versions.

**Q: How do I verify model integrity?**
A: Check the model hash in the ModelRegistry. Calculate the hash of the model code and compare.

**Q: What happens to old allocations when model upgrades?**
A: Old allocations remain valid. New allocations use the new model version.

### Security Questions

**Q: Is my data private?**
A: Allocation decisions and proofs are public. For private deposits, use MIST.cash integration.

**Q: Can proofs be forged?**
A: No, STARK proofs are cryptographically secure and cannot be forged.

**Q: What if the backend is compromised?**
A: Even if the backend is compromised, on-chain verification ensures only valid proofs can execute. Invalid proofs will be rejected.

**Q: Who controls the contracts?**
A: Contracts have owner addresses. DAO constraints are managed by the DAO. See contract addresses for details.

## Getting Help

### Support Channels

1. **Documentation:**
   - Review this troubleshooting guide
   - Check other documentation sections
   - Search for specific topics

2. **Logs:**
   - Check backend logs
   - Review transaction logs
   - Examine error messages

3. **Community:**
   - GitHub Issues
   - Discord (if available)
   - Forum (if available)

4. **Direct Support:**
   - Contact support email
   - Provide error details
   - Include proof hashes and transaction IDs

### Reporting Issues

When reporting issues, include:

1. **Error Details:**
   - Exact error message
   - When it occurred
   - Steps to reproduce

2. **System Information:**
   - Browser and version
   - Wallet type and version
   - Network (Sepolia/mainnet)

3. **Transaction Information:**
   - Transaction hash
   - Proof hash (if available)
   - Block number

4. **Logs:**
   - Backend logs (if accessible)
   - Browser console errors
   - Wallet transaction details

## Next Steps

- **[Getting Started](01-getting-started.md)** - Back to basics
- **[Executing Allocations](02-executing-allocations.md)** - Allocation process
- **[Viewing Transparency](03-viewing-transparency.md)** - Transparency features
- **[Architecture Deep Dive](../03-architecture/01-system-overview.md)** - Technical details

---

**Remember:** Most issues can be resolved by checking logs, verifying network connectivity, and ensuring services are running properly.
