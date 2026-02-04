#!/bin/bash
# Step 2: Diff our proof/public_input vs. Integrity's recursive example
# This identifies which field(s) are off

set -e

REPO_ROOT="/opt/obsqra.starknet"
EXAMPLE_PROOF="$REPO_ROOT/integrity/examples/proofs/recursive/cairo0_stone5_keccak_160_lsb_example_proof.json"

echo "=== Step 2: Compare Proof Structures ==="
echo ""
echo "Comparing our proof/public_input with Integrity's recursive example"
echo ""

# Find our most recent proof
OUR_PROOF=$(find /tmp -name "risk_proof.json" -type f -mmin -60 2>/dev/null | head -1)
OUR_PUBLIC=$(find /tmp -name "risk_public.json" -type f -mmin -60 2>/dev/null | head -1)

if [ -z "$OUR_PROOF" ] && [ -z "$OUR_PUBLIC" ]; then
    echo "⚠️  No recent proof/public input found in /tmp"
    echo "   Run a test first to generate proof files"
    exit 1
fi

echo "=== Example Proof Structure ==="
echo ""
echo "Top-level keys:"
jq 'keys' "$EXAMPLE_PROOF" 2>/dev/null

echo ""
echo "Public Input:"
echo "  Layout: $(jq -r '.public_input.layout' "$EXAMPLE_PROOF" 2>/dev/null)"
echo "  n_steps: $(jq -r '.public_input.n_steps' "$EXAMPLE_PROOF" 2>/dev/null)"
echo "  Memory segments: $(jq -r '.public_input.memory_segments | keys | join(", ")' "$EXAMPLE_PROOF" 2>/dev/null)"
echo "  Public memory count: $(jq -r '.public_input.public_memory | length' "$EXAMPLE_PROOF" 2>/dev/null)"

echo ""
echo "=== Our Proof Structure ==="
if [ -n "$OUR_PROOF" ]; then
    echo "Found: $OUR_PROOF"
    echo ""
    echo "Top-level keys:"
    jq 'keys' "$OUR_PROOF" 2>/dev/null || echo "Failed to read"
    
    if jq -e '.public_input' "$OUR_PROOF" >/dev/null 2>&1; then
        echo ""
        echo "Public Input (from proof):"
        echo "  Layout: $(jq -r '.public_input.layout // "N/A"' "$OUR_PROOF" 2>/dev/null)"
        echo "  n_steps: $(jq -r '.public_input.n_steps // "N/A"' "$OUR_PROOF" 2>/dev/null)"
        echo "  Memory segments: $(jq -r '.public_input.memory_segments | keys | join(", ") // "N/A"' "$OUR_PROOF" 2>/dev/null)"
    fi
fi

if [ -n "$OUR_PUBLIC" ]; then
    echo ""
    echo "=== Our Public Input (standalone) ==="
    echo "Found: $OUR_PUBLIC"
    echo ""
    echo "Public Input:"
    echo "  Layout: $(jq -r '.layout // "N/A"' "$OUR_PUBLIC" 2>/dev/null)"
    echo "  n_steps: $(jq -r '.n_steps // "N/A"' "$OUR_PUBLIC" 2>/dev/null)"
    echo "  Memory segments: $(jq -r '.memory_segments | keys | join(", ") // "N/A"' "$OUR_PUBLIC" 2>/dev/null)"
    echo "  Public memory count: $(jq -r '.public_memory | length // "N/A"' "$OUR_PUBLIC" 2>/dev/null)"
    
    echo ""
    echo "=== Detailed Comparison ==="
    echo ""
    echo "Memory Segments Structure:"
    echo "Example:"
    jq '.public_input.memory_segments' "$EXAMPLE_PROOF" 2>/dev/null | head -30
    echo ""
    echo "Ours:"
    jq '.memory_segments' "$OUR_PUBLIC" 2>/dev/null | head -30
fi

echo ""
echo "=== Checklist ==="
echo ""
echo "Compare these fields:"
echo "  [ ] layout (should be 'recursive')"
echo "  [ ] n_steps"
echo "  [ ] memory_segments structure"
echo "  [ ] memory_segments order"
echo "  [ ] builtin segments present (bitwise for us, ecdsa for example?)"
echo "  [ ] public_memory format"
echo "  [ ] rc_min, rc_max"
echo ""
