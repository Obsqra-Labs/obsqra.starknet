# Obsqra Demo Frontend

Simple, clean demo frontend showcasing ZKML features and Starknet novelty.

## Features

- **Stone Prover Proof Generation**: Live proof generation with real-time status
- **Constraint Verification**: Shows how DAO constraints are verified in proofs
- **Cost Calculator**: Demonstrates 95% cost savings with local Stone prover
- **MIST Privacy Integration**: Explains privacy + verifiability (mainnet fork note)
- **Novel Features Comparison**: Table showing why this is impossible on Ethereum

## Quick Start

1. **Start the backend** (if not already running):
   ```bash
   cd /opt/obsqra.starknet/backend
   # Start backend on port 8001
   ```

2. **Serve the demo frontend**:
   ```bash
   cd /opt/obsqra.starknet/demo-frontend/src
   python3 -m http.server 8080
   ```

3. **Open in browser**:
   ```
   http://localhost:8080
   ```

## Architecture

- **Vanilla JavaScript**: No framework complexity
- **ES6 Modules**: Clean component structure
- **Single Page**: All features on one page
- **Responsive**: Works on mobile and desktop

## Components

- `ProofGenerator.js`: Generates STARK proofs via API
- `ConstraintVerifier.js`: Shows constraint verification status
- `CostCalculator.js`: Calculates and displays cost savings
- `MistDemo.js`: Explains MIST.cash privacy integration
- `demo.js`: Main orchestrator

## API Endpoints

- `POST /api/v1/demo/generate-proof`: Generate proof for demo
- `GET /api/v1/demo/cost-comparison`: Get cost comparison data

## Notes

- MIST.cash is mainnet-only (use fork for testing)
- Stone prover requires local binary (falls back to LuminAIR if unavailable)
- Backend must be running on port 8001

## Design Philosophy

Based on Shramee's (MIST.cash) feedback:
- ✅ Simple, at-a-glance dashboard
- ✅ Quick action buttons
- ✅ Real returns/performance focus
- ✅ Provable model showcase
