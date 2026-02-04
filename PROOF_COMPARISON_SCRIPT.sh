#!/bin/bash
# Compare our proof/public input with Integrity's example

set -e

REPO_ROOT="/opt/obsqra.starknet"
EXAMPLE_PROOF="$REPO_ROOT/integrity/examples/proofs/dex/cairo0_stone5_keccak_160_lsb_example_proof.json"

echo "=== Integrity Example Proof Structure ==="
echo ""
echo "Top-level keys:"
jq 'keys' "$EXAMPLE_PROOF" 2>/dev/null || echo "Failed to read example proof"

echo ""
echo "Public Input keys:"
jq '.public_input | keys' "$EXAMPLE_PROOF" 2>/dev/null || echo "No public_input"

echo ""
echo "Public Input structure:"
jq '.public_input' "$EXAMPLE_PROOF" 2>/dev/null | head -100

echo ""
echo "Unsent Commitment keys:"
jq '.unsent_commitment | keys' "$EXAMPLE_PROOF" 2>/dev/null || echo "No unsent_commitment"

echo ""
echo "OODS values count:"
jq '.unsent_commitment.oods_values | length' "$EXAMPLE_PROOF" 2>/dev/null || echo "No oods_values"

echo ""
echo "=== Finding Our Recent Proof ==="
find /tmp -name "risk_proof.json" -type f -mmin -60 2>/dev/null | head -1 | while read PROOF; do
    echo "Found: $PROOF"
    echo ""
    echo "Our Proof keys:"
    jq 'keys' "$PROOF" 2>/dev/null || echo "Failed to read"
    
    echo ""
    echo "Our Public Input (if embedded):"
    jq '.public_input | keys' "$PROOF" 2>/dev/null || echo "No public_input in proof"
done

echo ""
echo "=== Finding Our Recent Public Input ==="
find /tmp -name "risk_public.json" -type f -mmin -60 2>/dev/null | head -1 | while read PUBLIC; do
    echo "Found: $PUBLIC"
    echo ""
    echo "Our Public Input:"
    cat "$PUBLIC" | jq . 2>/dev/null || echo "Failed to read"
done
