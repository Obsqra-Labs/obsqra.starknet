#!/bin/bash
# Stone Prover FRI Parameter Testing - Bash Script
# Use this if you need quick manual testing or debugging

set -e

# Configuration
PROVER="/opt/obsqra.starknet/stone-prover/build/bazelout/k8-opt/bin/src/starkware/main/cpu/cpu_air_prover"
PARAMS_FILE="/opt/obsqra.starknet/integrity/examples/proofs/cpu_air_params.json"
TRACE_FILE="${1:-}"
TEST_DIR="/tmp/stone_fri_tests"

if [ -z "$TRACE_FILE" ]; then
    echo "Usage: $0 <trace_file>"
    echo ""
    echo "Example:"
    echo "  $0 /opt/obsqra.starknet/test_trace.json"
    exit 1
fi

if [ ! -f "$TRACE_FILE" ]; then
    echo "Error: Trace file not found: $TRACE_FILE"
    exit 1
fi

mkdir -p "$TEST_DIR"

echo "=================================================="
echo "Stone Prover FRI Parameter Testing"
echo "=================================================="
echo "Trace file: $TRACE_FILE"
echo "Size: $(du -h "$TRACE_FILE" | cut -f1)"
echo "Test directory: $TEST_DIR"
echo ""

# Test parameters for 131,072 steps
# Format: "last_layer fri_step_list"
TEST_CASES=(
    "32 [4,4,4,4]"
    "64 [3,4,4,4]"
    "128 [3,3,4,4]"
    "256 [3,3,3,4]"
    "512 [3,3,3,3]"
    "1024 [3,3,3,2]"
)

PASSED=0
FAILED=0

for i in "${!TEST_CASES[@]}"; do
    TEST=${TEST_CASES[$i]}
    LAST_LAYER=$(echo "$TEST" | awk '{print $1}')
    FRI_STEPS=$(echo "$TEST" | awk '{print $2}')
    
    TEST_NUM=$((i + 1))
    OUTPUT_FILE="$TEST_DIR/proof_$TEST_NUM.json"
    LOG_FILE="$TEST_DIR/test_$TEST_NUM.log"
    
    echo ""
    echo "Test $TEST_NUM/$((${#TEST_CASES[@]})): last_layer=$LAST_LAYER, fri_steps=$FRI_STEPS"
    
    START=$(date +%s%N)
    
    if "$PROVER" \
        --input_file "$TRACE_FILE" \
        --output_file "$OUTPUT_FILE" \
        --parameter_file "$PARAMS_FILE" \
        --last_layer_degree_bound "$LAST_LAYER" \
        --fri_step_list "$FRI_STEPS" \
        --generate_annotations \
        > "$LOG_FILE" 2>&1; then
        
        END=$(date +%s%N)
        ELAPSED_MS=$(( (END - START) / 1000000 ))
        ELAPSED_S=$(echo "scale=1; $ELAPSED_MS / 1000" | bc)
        
        PROOF_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo "  ✅ SUCCESS in ${ELAPSED_S}s, proof size: $PROOF_SIZE"
        PASSED=$((PASSED + 1))
    else
        END=$(date +%s%N)
        ELAPSED_MS=$(( (END - START) / 1000000 ))
        ELAPSED_S=$(echo "scale=1; $ELAPSED_MS / 1000" | bc)
        
        LAST_ERROR=$(tail -5 "$LOG_FILE" | grep -i "error\|abort\|assert" | head -1)
        echo "  ❌ FAILED in ${ELAPSED_S}s"
        if [ -n "$LAST_ERROR" ]; then
            echo "     Error: $LAST_ERROR"
        fi
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=================================================="
echo "SUMMARY"
echo "=================================================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $PASSED -gt 0 ]; then
    echo "📊 Working parameter sets found! Check $TEST_DIR for details."
    exit 0
else
    echo "🚨 No working parameters found. Check $TEST_DIR for detailed logs."
    exit 1
fi
