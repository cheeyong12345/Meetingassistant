#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

# Try to use virtual environment, fallback to system Python
venv_python = script_dir / "venv" / "bin" / "python3"
if venv_python.exists():
    python_cmd = str(venv_python)
    print(f"Using virtual environment: {python_cmd}")
else:
    python_cmd = sys.executable
    print(f"Virtual environment not found, using system Python: {python_cmd}")

# Run CLI with arguments
cmd = [python_cmd, "cli.py"] + sys.argv[1:]
subprocess.run(cmd)
