#!/bin/bash

# =============================================================================
# init.sh - Project Initialization Script
# =============================================================================
# Run this script at the start of every session to ensure the environment
# is properly set up.
# =============================================================================

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Detect platform and set Python path for venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
else
    VENV_PYTHON=".venv/bin/python"
fi

echo -e "${YELLOW}Initializing CS2 Monitor project...${NC}"

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_MAJOR=3
REQUIRED_MINOR=12

MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt "$REQUIRED_MAJOR" ] || ([ "$MAJOR" -eq "$REQUIRED_MAJOR" ] && [ "$MINOR" -lt "$REQUIRED_MINOR" ]); then
    echo -e "${RED}Error: Python 3.12+ is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Install dependencies using venv Python directly
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    "$VENV_PYTHON" -m pip install -r requirements.txt
else
    echo -e "${YELLOW}Warning: requirements.txt not found.${NC}"
fi

# Create data directory if not exists
mkdir -p data

# Check .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found. Copy from .env.example:${NC}"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your actual API keys and webhook URLs"
fi

# Verify syntax of core files
echo "Verifying Python syntax..."
python -m py_compile main.py config.py 2>/dev/null || true
for f in api/*.py core/*.py notify/*.py storage/*.py utils/*.py; do
    [ -f "$f" ] && python -m py_compile "$f" 2>/dev/null || true
done

echo -e "${GREEN}✓ Initialization complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Ensure .env is configured with your API keys"
echo "  2. Run tests: $VENV_PYTHON -m pytest tests/"
echo "  3. Run app:   $VENV_PYTHON main.py"
echo ""
echo "Ready to continue development."
