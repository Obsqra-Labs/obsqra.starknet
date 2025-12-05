#!/bin/bash
# Setup script for Obsqra.starknet development environment
# This script sets up Rust, Cairo, and Scarb without interfering with existing Anvil/Foundry setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Obsqra.starknet development environment${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "contracts/Scarb.toml" ]; then
    echo -e "${RED}❌ Error: Please run this script from the obsqra.starknet root directory${NC}"
    exit 1
fi

# 1. Check Rust installation
echo -e "${BLUE}📦 Checking Rust installation...${NC}"
if command -v rustc &> /dev/null && command -v cargo &> /dev/null; then
    RUST_VERSION=$(rustc --version)
    echo -e "${GREEN}✅ Rust is installed: $RUST_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Rust not found. Installing Rust...${NC}"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    echo -e "${GREEN}✅ Rust installed${NC}"
fi

# 2. Check/Install Scarb (Cairo package manager)
echo -e "${BLUE}📦 Checking Scarb installation...${NC}"
if command -v scarb &> /dev/null; then
    SCARB_VERSION=$(scarb --version)
    echo -e "${GREEN}✅ Scarb is installed: $SCARB_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Scarb not found. Installing Scarb...${NC}"
    curl --proto '=https' --tlsv1.2 -sSf https://docs.swmansion.com/scarb/install.sh | sh
    source "$HOME/.cargo/env"
    echo -e "${GREEN}✅ Scarb installed${NC}"
fi

# 3. Check Node.js
echo -e "${BLUE}📦 Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js is installed: $NODE_VERSION${NC}"
    
    # Check version (need 18+)
    NODE_MAJOR=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_MAJOR" -lt 18 ]; then
        echo -e "${YELLOW}⚠️  Node.js version is $NODE_VERSION, but we recommend 18+${NC}"
    fi
else
    echo -e "${RED}❌ Error: Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# 4. Check Python
echo -e "${BLUE}📦 Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python is installed: $PYTHON_VERSION${NC}"
    
    # Check version (need 3.10+)
    PYTHON_MAJOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1)
    PYTHON_MINOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        echo -e "${YELLOW}⚠️  Python version is $PYTHON_VERSION, but we recommend 3.10+${NC}"
    fi
else
    echo -e "${RED}❌ Error: Python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# 5. Verify Cairo installation via Scarb
echo -e "${BLUE}🔍 Verifying Cairo installation...${NC}"
if scarb --version &> /dev/null; then
    echo -e "${GREEN}✅ Cairo toolchain is accessible via Scarb${NC}"
else
    echo -e "${RED}❌ Error: Cairo toolchain not working. Try: scarb --version${NC}"
    exit 1
fi

# 6. Set up contracts
echo -e "${BLUE}📝 Setting up Cairo contracts...${NC}"
cd contracts
if scarb build 2>&1 | grep -q "error"; then
    echo -e "${YELLOW}⚠️  Contracts have compilation issues (this is expected for starter code)${NC}"
else
    echo -e "${GREEN}✅ Contracts build successfully${NC}"
fi
cd ..

# 7. Set up frontend dependencies
echo -e "${BLUE}📝 Setting up frontend dependencies...${NC}"
if [ -d "frontend" ]; then
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing npm packages..."
        npm install --legacy-peer-deps
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ Frontend dependencies already installed${NC}"
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  Frontend directory not found${NC}"
fi

# 8. Set up AI service
echo -e "${BLUE}📝 Setting up AI service...${NC}"
if [ -d "ai-service" ]; then
    cd ai-service
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ AI service dependencies installed${NC}"
    else
        echo -e "${GREEN}✅ AI service virtual environment already exists${NC}"
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  AI service directory not found${NC}"
fi

# 9. Check for Starknet Foundry (snforge)
echo -e "${BLUE}📦 Checking Starknet Foundry (snforge)...${NC}"
if command -v snforge &> /dev/null; then
    echo -e "${GREEN}✅ Starknet Foundry is installed${NC}"
else
    echo -e "${YELLOW}⚠️  Starknet Foundry (snforge) not found${NC}"
    echo -e "${BLUE}   Install with: scarb install snforge_std${NC}"
    echo -e "${BLUE}   Or: cargo install --git https://github.com/foundry-rs/starknet-foundry snforge${NC}"
fi

echo ""
echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. cd contracts && scarb build"
echo "  2. cd contracts && snforge test  (if snforge is installed)"
echo "  3. cd frontend && npm run dev"
echo "  4. cd ai-service && source venv/bin/activate && python main.py"
echo ""
echo -e "${YELLOW}Note: This setup does not interfere with your existing Anvil/Foundry setup${NC}"
echo -e "${YELLOW}      Rust/Cargo are shared, but Cairo/Scarb are separate tools${NC}"

