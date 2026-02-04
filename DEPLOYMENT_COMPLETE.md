# FactRegistry Deployment Complete ✅

## Option 1: Testing (Existing Contract) ✅

**Status**: Tested and working
- **Address**: `0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c`
- **Test Result**: Contract is accessible and responds to calls
- **Cost**: Just gas fees (no credits needed)
- **Ready to use**: Yes

## Option 2: Your Own Deployment ✅

**Status**: Successfully deployed!

### Deployment Details
- **Contract Address**: `0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64`
- **Class Hash**: `0x00607244d8e0d390232dbda6ab013807a7b6675d60719e9427b4674c09a1ccfd`
- **Owner**: `0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d`
- **Network**: Starknet Sepolia
- **Transaction Hash**: `0x04d9c4bf760c392c438ed921b5b53730789556c31ef9d727e220ef2c0aae9896`

### Links
- **Contract**: https://sepolia.starkscan.co/contract/0x063feefb4b7cfb46b89d589a8b00bceb7905a7d51c4e8068d4b45e0d9d018f64
- **Transaction**: https://sepolia.starkscan.co/tx/0x04d9c4bf760c392c438ed921b5b53730789556c31ef9d727e220ef2c0aae9896
- **Class**: https://sepolia.starkscan.co/class/0x00607244d8e0d390232dbda6ab013807a7b6675d60719e9427b4674c09a1ccfd

### Configuration Updated
✅ `backend/app/services/integrity_service.py` - Updated `INTEGRITY_VERIFIER_SEPOLIA`
✅ `backend/app/api/routes/risk_engine.py` - Updated `SHARP_FACT_REGISTRY_SEPOLIA`

### How It Was Fixed
1. Removed `url` from `integrity/snfoundry.toml` to allow `--network=sepolia` flag
2. Used `--network=sepolia` syntax per [Starknet Sepolia docs](https://docs.starknet.io/build/quickstart/sepolia)
3. Waited 30 seconds for declaration to propagate before deployment
4. Used full 66-character class hash (with leading zeros)

### Next Steps
1. ✅ Backend config updated - restart backend to use new contract
2. Test proof verification with your deployed contract
3. Monitor contract on Starkscan

## Summary

Both options are now available:
- **Option 1**: Tested and ready (existing contract)
- **Option 2**: Deployed and configured (your own contract)

Your backend is now configured to use **Option 2** (your own deployment).
To switch back to Option 1, uncomment the old addresses in the config files.
