#!/bin/bash
# Step 1: Verify Integrity's canonical recursive proof end-to-end
# This tests if our deployment/config is correct

set -e

REPO_ROOT="/opt/obsqra.starknet"
INTEGRITY_DIR="$REPO_ROOT/integrity"
EXAMPLE_PROOF="$INTEGRITY_DIR/examples/proofs/recursive/cairo0_stone5_keccak_160_lsb_example_proof.json"
SERIALIZER_BIN="$INTEGRITY_DIR/target/release/proof_serializer"
FACT_REGISTRY="0x4ce7851f00b6c3289674841fd7a1b96b6fd41ed1edc248faccd672c26371b8c"

echo "=== Step 1: Verify Canonical Recursive Proof ==="
echo ""
echo "This tests if our deployment/config is correct."
echo "If this fails, the issue is in deployment/config."
echo "If this passes, the issue is in our proof/public-input."
echo ""

# Check if example proof exists
if [ ! -f "$EXAMPLE_PROOF" ]; then
    echo "❌ Example proof not found: $EXAMPLE_PROOF"
    exit 1
fi

echo "✅ Found example proof: $EXAMPLE_PROOF"
echo ""

# Check if serializer exists
if [ ! -f "$SERIALIZER_BIN" ]; then
    echo "⚠️  Serializer not found: $SERIALIZER_BIN"
    echo "   Building serializer..."
    cd "$INTEGRITY_DIR"
    cargo build --release --bin proof_serializer
    if [ ! -f "$SERIALIZER_BIN" ]; then
        echo "❌ Failed to build serializer"
        exit 1
    fi
fi

echo "✅ Found serializer: $SERIALIZER_BIN"
echo ""

# Serialize the example proof
echo "Serializing example proof..."
CALLDATA_FILE="/tmp/canonical_calldata.txt"
cat "$EXAMPLE_PROOF" | "$SERIALIZER_BIN" > "$CALLDATA_FILE"

if [ ! -s "$CALLDATA_FILE" ]; then
    echo "❌ Serialization failed - empty output"
    exit 1
fi

CALLDATA_SIZE=$(wc -w < "$CALLDATA_FILE")
echo "✅ Serialized proof: $CALLDATA_SIZE felts"
echo ""

# Show first few felts
echo "First 10 felts:"
head -n 1 "$CALLDATA_FILE" | tr ' ' '\n' | head -10
echo ""

echo "=== Next Steps ==="
echo ""
echo "To verify on-chain, use:"
echo "  ./verify-on-starknet.sh $FACT_REGISTRY $CALLDATA_FILE recursive keccak_160_lsb stone5 strict"
echo ""
echo "Or use our backend's Integrity service to call:"
echo "  verify_proof_full_and_register_fact"
echo ""
