#!/bin/bash
# Run zkde.fi E2E test suite

cd "$(dirname "$0")"
source backend/venv/bin/activate
export STARKNET_RPC_URL="https://starknet-sepolia.g.alchemy.com/starknet/version/rpc/v0_7/EvhYN6geLrdvbYHVRgPJ7"
python3 tests/e2e_test_suite.py "$@"
