# Owner Wallet Setup Guide

## Overview

The integration tests include owner-only functions that require the contract owner's wallet to execute. Since the contract owner is set during deployment and cannot be changed without redeploying, we've implemented a backend API route that can execute these functions using the owner's private key.

## Setup Instructions

### Automatic Setup (Recommended)

The API route automatically reads the owner's private key from the sncast keystore file at:
- `/root/.starknet_accounts/starknet_open_zeppelin_accounts.json`

The deployer account profile is used, which matches the contract owner address:
- **Owner Address**: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`
- **Account Profile**: `deployer` (in `alpha-sepolia` network)

**No additional setup required!** The API will automatically find and use the private key from the keystore.

### Manual Setup (Optional)

If you prefer to use an environment variable instead, you can add it to `frontend/.env.local`:

```bash
# Owner's private key for executing owner-only functions via backend
OWNER_PRIVATE_KEY=0x...your_private_key_here...
```

**Note**: If `OWNER_PRIVATE_KEY` is set, it takes precedence over the keystore file.

**⚠️ Security Note**: 
- Never commit private keys to version control
- Add `.env.local` to `.gitignore` if not already there
- This private key should only be used for testing/demo purposes
- In production, use a more secure key management solution

## How It Works

### Frontend Toggle

The Integration Tests page now includes a "Wallet Mode" toggle:

- **Your Wallet**: Executes transactions using your connected wallet (default)
- **Owner Wallet**: Executes owner-only functions via the backend API using the owner's private key

### Owner-Only Functions

These functions require owner access:
- `deploy_to_protocols()` - Deploy pending deposits to protocols
- `test_jediswap_only()` - Test JediSwap integration
- `test_ekubo_only()` - Test Ekubo integration

### Public Functions

These functions work with any wallet:
- `deposit()` - Deposit funds
- `withdraw()` - Withdraw funds

## API Route

The backend API route is located at:
- **Path**: `/api/integration-tests/execute-as-owner`
- **Method**: POST
- **Body**: 
  ```json
  {
    "functionName": "deploy_to_protocols",
    "calldata": []
  }
  ```

## Troubleshooting

### Error: "OWNER_PRIVATE_KEY environment variable not set"

**Solution**: Make sure you've added `OWNER_PRIVATE_KEY` to your `.env.local` file and restarted the server.

### Error: "Transaction execution has failed: Unauthorized"

**Solution**: 
1. Make sure you're using "Owner Wallet" mode for owner-only functions
2. Verify the `OWNER_PRIVATE_KEY` matches the contract owner address
3. Check that the private key is correctly formatted (should start with `0x`)

### Error: "Account not found" or "Invalid private key"

**Solution**: 
- Verify the private key format is correct
- Ensure the private key corresponds to the owner address: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`

## Security Considerations

1. **Never expose private keys**: Keep `.env.local` out of version control
2. **Use separate keys**: Don't use production keys for testing
3. **Rotate keys**: If a key is ever exposed, rotate it immediately
4. **Limit access**: Only trusted developers should have access to owner keys
5. **Consider alternatives**: For production, consider:
   - Hardware wallets
   - Key management services (AWS KMS, HashiCorp Vault)
   - Multi-sig wallets
   - Account abstraction with social recovery

## Alternative: Make Your Wallet the Owner

If you want to make your wallet (`0x0199F1c59ffb4403E543B384f8BC77cF390A8671FBBC0F6f7eae0D462b39B777`) the contract owner, you would need to:

1. Redeploy the contract with your wallet address as the owner in the constructor
2. Update the contract address in the frontend configuration

This requires redeploying the contract, which is why we implemented the backend API solution instead.

