#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
echo "Testing microphone devices..."
python3 cli.py devices
echo ""
echo "Testing engines..."
python3 cli.py test
