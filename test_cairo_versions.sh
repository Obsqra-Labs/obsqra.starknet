#!/bin/bash
# Automated Cairo Version Tester for CASM Hash Mismatch Resolution
# Purpose: Find Cairo version that produces CASM hash 0x4120dfff... expected by PublicNode RPC

set -e

# Configuration
TARGET_HASH="0x4120dfff561b2868ae271da2cfb031a4c0570d5bb9afd2c232b94088f457492"
CONTRACT_NAME="StrategyRouterV2"
PROJECT_DIR="/opt/obsqra.starknet/contracts"
SCARB_TOML="$PROJECT_DIR/Scarb.toml"
BACKUP_TOML="${SCARB_TOML}.backup"
LOG_DIR="/tmp/cairo_version_test"
RESULTS_FILE="$LOG_DIR/results.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Create log directory
mkdir -p "$LOG_DIR"

# Versions to test (in priority order - most likely first)
VERSIONS=("2.10.1" "2.10.0" "2.9.2" "2.9.1" "2.8.4" "2.8.0" "2.7.0" "2.6.0")

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Cairo Version Binary Search for CASM Hash Match${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Target CASM Hash: ${YELLOW}$TARGET_HASH${NC}"
echo -e "Contract: ${YELLOW}$CONTRACT_NAME${NC}"
echo -e "Project: ${YELLOW}$PROJECT_DIR${NC}"
echo ""

# Backup Scarb.toml
if [ ! -f "$BACKUP_TOML" ]; then
    echo -e "${YELLOW}Backing up Scarb.toml...${NC}"
    cp "$SCARB_TOML" "$BACKUP_TOML"
fi

# Initialize results file
echo "Cairo Version Test Results" > "$RESULTS_FILE"
echo "Target Hash: $TARGET_HASH" >> "$RESULTS_FILE"
echo "Started: $(date)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

cd "$PROJECT_DIR"

MATCH_FOUND=false

for version in "${VERSIONS[@]}"; do
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Testing Cairo $version${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    
    # Update Scarb.toml with version
    echo -e "${YELLOW}Updating Scarb.toml to Cairo $version...${NC}"
    
    # Use sed to update starknet dependency version
    # This assumes Scarb.toml has: starknet = ">=2.0.0" or similar
    sed -i.tmp "s/starknet = \">=[0-9.]*\"/starknet = \">=$version\"/" "$SCARB_TOML" || {
        echo -e "${RED}Failed to update Scarb.toml${NC}"
        continue
    }
    rm -f "${SCARB_TOML}.tmp"
    
    # Clean build
    echo -e "${YELLOW}Cleaning previous build...${NC}"
    scarb clean > /dev/null 2>&1 || true
    rm -rf Scarb.lock target/ 2>/dev/null || true
    
    # Build
    echo -e "${YELLOW}Building with Cairo $version...${NC}"
    BUILD_LOG="$LOG_DIR/cairo_${version}_build.log"
    
    if scarb build 2>&1 | tee "$BUILD_LOG" > /dev/null; then
        echo -e "${GREEN}✅ Build successful${NC}"
        
        # Extract CASM hash
        CASM_FILE="target/dev/obsqra_contracts_${CONTRACT_NAME}.compiled_contract_class.json"
        
        if [ -f "$CASM_FILE" ]; then
            # Try jq first, fallback to grep
            if command -v jq &> /dev/null; then
                HASH=$(jq -r '.compiled_class_hash' "$CASM_FILE" 2>/dev/null || echo "")
            else
                HASH=$(grep -oP '"compiled_class_hash"\s*:\s*"\K0x[a-fA-F0-9]{64}' "$CASM_FILE" 2>/dev/null | head -1 || echo "")
            fi
            
            if [ -n "$HASH" ] && [ "$HASH" != "null" ]; then
                echo -e "${CYAN}Cairo $version produces CASM hash:${NC} ${YELLOW}$HASH${NC}"
                echo "Cairo $version: $HASH" >> "$RESULTS_FILE"
                
                if [ "$HASH" = "$TARGET_HASH" ]; then
                    echo ""
                    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
                    echo -e "${GREEN}  ✅ MATCH FOUND!${NC}"
                    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
                    echo ""
                    echo -e "${GREEN}Cairo $version produces the expected hash!${NC}"
                    echo -e "${CYAN}Solution: Use Cairo $version for deployment${NC}"
                    echo ""
                    echo "Cairo $version: MATCH ✅" >> "$RESULTS_FILE"
                    echo "Solution: Use Cairo $version" >> "$RESULTS_FILE"
                    
                    MATCH_FOUND=true
                    break
                else
                    echo -e "${RED}❌ Hash mismatch. Continuing...${NC}"
                fi
            else
                echo -e "${RED}⚠️  Could not extract CASM hash from $CASM_FILE${NC}"
                echo "Cairo $version: Hash extraction failed" >> "$RESULTS_FILE"
            fi
        else
            echo -e "${RED}⚠️  CASM file not found: $CASM_FILE${NC}"
            echo "Cairo $version: CASM file not found" >> "$RESULTS_FILE"
        fi
    else
        echo -e "${RED}❌ Build failed. Check logs: $BUILD_LOG${NC}"
        echo "Cairo $version: Build failed" >> "$RESULTS_FILE"
    fi
    
    echo ""
done

# Restore original Scarb.toml
if [ -f "$BACKUP_TOML" ]; then
    echo -e "${YELLOW}Restoring original Scarb.toml...${NC}"
    cp "$BACKUP_TOML" "$SCARB_TOML"
fi

# Final summary
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
if [ "$MATCH_FOUND" = true ]; then
    echo -e "${GREEN}  ✅ SUCCESS: Matching Cairo version found${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Update Scarb.toml to use the matching Cairo version"
    echo "2. Rebuild: scarb clean && scarb build"
    echo "3. Declare: sncast --account deployer declare --contract-name StrategyRouterV2 --network sepolia"
    echo ""
    echo -e "${GREEN}Results saved to: $RESULTS_FILE${NC}"
    exit 0
else
    echo -e "${RED}  ❌ NO MATCH FOUND${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}No matching version found in tested range.${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Check PublicNode RPC version directly"
    echo "2. Try alternative RPC endpoints (Alchemy, Infura)"
    echo "3. Contact PublicNode support for their Cairo version"
    echo "4. Review results: $RESULTS_FILE"
    echo ""
    echo -e "${CYAN}All test logs saved to: $LOG_DIR${NC}"
    exit 1
fi
