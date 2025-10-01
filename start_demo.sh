#!/bin/bash
# Start Demo Script for Meeting Assistant
# This script activates the virtual environment and starts the web app

set -e  # Exit on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Meeting Assistant Demo Starter"
echo "========================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run one of the installation scripts first:"
    echo "  python3 install_sbc.py         # Full installation"
    echo "  python3 install_lightweight.py # Minimal installation"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Set PYTHONPATH to include the project root
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
echo "PYTHONPATH set to: $PYTHONPATH"
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "Warning: config.yaml not found!"
    echo "The application may not start correctly."
    echo ""
fi

# Start the web application
echo "Starting Meeting Assistant Web Interface..."
echo "========================================="
echo ""

python3 web_app.py
