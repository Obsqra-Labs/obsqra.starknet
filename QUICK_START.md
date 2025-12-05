# Quick Start Guide

## ✅ What's Ready

1. **Contracts** - All compile successfully
2. **Test Suite** - 28 tests ready (need snforge to run)
3. **Frontend** - Structure complete, installing dependencies...
4. **AI Service** - Code complete, installing dependencies...

## Run These Commands

### Contracts (Already Working!)
```bash
cd /opt/obsqra.starknet/contracts
scarb build  # ✅ Compiles!
```

### Frontend
```bash
cd /opt/obsqra.starknet/frontend
npm install --legacy-peer-deps  # Run this if not done
npm run dev  # Start dev server
```

### AI Service
```bash
cd /opt/obsqra.starknet/ai-service
source venv/bin/activate
pip install -r requirements.txt  # Run this if not done
python main.py  # Start service
```

### Tests (Once snforge installed)
```bash
cd /opt/obsqra.starknet/contracts
snforge test  # Run all 28 tests
```

## 📊 Current Status

- ✅ Contracts: Compiling
- ✅ Tests: Written (28 tests)
- ⏳ Frontend: Installing deps
- ⏳ AI Service: Installing deps
- ⏳ snforge: Need to install

## 📝 Next Steps

1. Wait for npm/pip installs to complete
2. Install snforge for testing
3. Configure environment variables
4. Deploy to testnet
5. Run end-to-end tests

Everything is ready - just installing dependencies!
