# Strategy Router V2 - Testing Guide

## Contract Information

**Contract Address**: `0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e`  
**Network**: Starknet Sepolia  
**Class Hash**: `0x01afb6e5a5811eca06eddb043710aff0b2527055703d80d41f18325e40b332d8`  
**Explorer**: https://sepolia.starkscan.co/contract/0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e

## Testing Methods

### Option 1: Frontend Testing (Recommended)

1. **Update Frontend Configuration**:
   ```bash
   # Update .env.local in frontend directory
   NEXT_PUBLIC_STRATEGY_ROUTER_ADDRESS=0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Functions via UI**:
   - Connect wallet (Argent/Braavos)
   - Navigate to Dashboard
   - **Deposit**: Enter amount and click "Deposit STRK"
   - **Deploy**: Click "Deploy to Protocols" (after deposit)
   - **Withdraw**: Enter amount and click "Withdraw STRK"
   - **Integration Tests**: Navigate to "🧪 Integration Tests" tab

### Option 2: Command Line Testing (sncast)

**Note**: RPC version mismatch may cause issues. Wait 1-2 minutes after deployment for contract finalization.

1. **Check Allocation**:
   ```bash
   sncast --profile deployer call \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function get_allocation
   ```

2. **Check Position Counts**:
   ```bash
   # JediSwap positions
   sncast --profile deployer call \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function get_jediswap_position_count
   
   # Ekubo positions
   sncast --profile deployer call \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function get_ekubo_position_count
   ```

3. **Deposit STRK**:
   ```bash
   # First approve STRK (0.1 STRK = 100000000000000000 wei)
   sncast --profile deployer invoke \
       --contract-address 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d \
       --function approve \
       --calldata 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e 100000000000000000 0
   
   # Then deposit
   sncast --profile deployer invoke \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function deposit \
       --calldata 100000000000000000 0
   ```

4. **Deploy to Protocols**:
   ```bash
   sncast --profile deployer invoke \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function deploy_to_protocols
   ```

5. **Check User Balance**:
   ```bash
   sncast --profile deployer call \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function get_user_balance \
       --calldata 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
   ```

6. **Accrue Yields** (after positions exist):
   ```bash
   sncast --profile deployer invoke \
       --contract-address 0x0456ae70b7b9c77522b4bef65a119ce4e8341be78c4007ceefd764685e7aad8e \
       --function accrue_yields
   ```

### Option 3: Automated Test Script

Run the comprehensive test script:
```bash
cd /opt/obsqra.starknet
./test-contract.sh
```

This script will:
1. Check allocation
2. Check position counts
3. Approve STRK
4. Deposit STRK
5. Deploy to protocols (with confirmation)
6. Check positions after deployment
7. Test accrue_yields (with confirmation)

## Expected Test Flow

1. **Initial State**:
   - Allocation: 50% JediSwap, 50% Ekubo (5000 basis points each)
   - Position counts: 0
   - Total deposits: 0

2. **After Deposit**:
   - User balance increases
   - Pending deposits increases
   - Total deposits increases

3. **After Deploy**:
   - JediSwap position count: 1
   - Ekubo position count: 1
   - Positions stored with metadata
   - Pending deposits decreases

4. **After Accrue Yields**:
   - Fees collected from both protocols
   - Total deposits increases (reinvestment)
   - YieldsAccrued event emitted

## Troubleshooting

### RPC Version Mismatch
If you see `RPC node uses incompatible version`, try:
- Wait 1-2 minutes for contract finalization
- Use a different RPC endpoint (Alchemy recommended)
- Update sncast configuration

### Contract Not Found
- Wait for transaction finalization (check on Starkscan)
- Verify contract address is correct
- Check network (must be Sepolia)

### Transaction Failures
- Ensure sufficient STRK balance
- Check token approvals
- Verify protocol addresses are correct
- Check transaction on Starkscan for detailed error

## Test Checklist

- [ ] Contract deployed and verified on Starkscan
- [ ] Allocation check (should be 50/50)
- [ ] STRK approval successful
- [ ] Deposit successful
- [ ] User balance updated
- [ ] Deploy to protocols successful
- [ ] JediSwap position created
- [ ] Ekubo position created
- [ ] Position metadata stored
- [ ] Accrue yields successful (if fees available)
- [ ] Withdraw successful

## Integration Test Tab

The frontend includes an "Integration Tests" tab that provides:
- Real-time status of all integrations
- Test buttons for each function
- Transaction hash tracking
- Status indicators (✅ completed, 🔄 in progress, ❌ blocked, 📋 planned)

Access via Dashboard → "🧪 Integration Tests" tab.
