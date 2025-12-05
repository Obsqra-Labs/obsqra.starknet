#!/bin/bash

set -e

echo "Running integration tests..."

# Build contracts
echo "Building contracts..."
cd contracts
scarb build

# Run tests
echo "Running tests..."
snforge test

echo "Integration tests complete!"

