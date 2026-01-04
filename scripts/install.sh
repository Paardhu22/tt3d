#!/bin/bash
# Installation Script for Tsuana 3D World Generator
# Run this with: bash install.sh

echo ""
echo "========================================"
echo "  TSUANA 3D World Generator"
echo "  Installation Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}[1/5] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        echo -e "  ${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
    else
        echo -e "  ${RED}✗ Python 3.8+ required (found $PYTHON_VERSION)${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

# Install dependencies
echo ""
echo -e "${YELLOW}[2/5] Installing Python packages...${NC}"
python3 -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "  ${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Setup .env file
echo ""
echo -e "${YELLOW}[3/5] Setting up environment file...${NC}"
if [ -f ".env" ]; then
    echo -e "  ${YELLOW}⚠ .env file already exists${NC}"
    read -p "  Overwrite? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.template .env
        echo -e "  ${GREEN}✓ .env file created${NC}"
    else
        echo -e "  ${YELLOW}→ Keeping existing .env${NC}"
    fi
else
    cp .env.template .env
    echo -e "  ${GREEN}✓ .env file created${NC}"
fi

# Create output directory
echo ""
echo -e "${YELLOW}[4/5] Creating output directory...${NC}"
if [ ! -d "output" ]; then
    mkdir output
    echo -e "  ${GREEN}✓ output/ directory created${NC}"
else
    echo -e "  ${YELLOW}→ output/ directory already exists${NC}"
fi

# Run setup check
echo ""
echo -e "${YELLOW}[5/5] Verifying installation...${NC}"
python3 setup_check.py

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Installation Complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Configure .env file (optional - uses defaults)"
echo "     cp .env.template .env"
echo "     Edit LOCAL_LLM_MODEL if needed"
echo ""
echo "  2. Start the API server:"
echo "     uvicorn app.api:app --host 0.0.0.0 --port 8000"
echo ""
echo "  3. Run example:"
echo "     python3 examples/generate_world_example.py"
echo ""
echo -e "${CYAN}📖 Read README.md for full documentation${NC}"
echo -e "${CYAN}🚀 Read QUICKSTART.md for quick start guide${NC}"
echo ""
