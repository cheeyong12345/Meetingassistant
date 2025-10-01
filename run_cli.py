#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

# Activate virtual environment
venv_python = script_dir / "venv" / "bin" / "python3"
if not venv_python.exists():
    print("Error: Virtual environment not found. Please run install_sbc.py first.")
    sys.exit(1)

# Run CLI with arguments
cmd = [str(venv_python), "cli.py"] + sys.argv[1:]
subprocess.run(cmd)
