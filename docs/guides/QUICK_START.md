# Quick Start Guide - Meeting Assistant

This guide will help you start the Meeting Assistant demo quickly.

## Prerequisites

1. Virtual environment should be set up (run installation script if not done)
2. All dependencies should be installed

## Starting the Demo

### Option 1: Using the Start Script (Recommended)

Simply run:

```bash
./start_demo.sh
```

This script will:
- Activate the virtual environment
- Set up the correct PYTHONPATH
- Start the web interface

### Option 2: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Start web app
python3 web_app.py
```

### Option 3: Using the run_web.py wrapper

```bash
./run_web.py
```

## Accessing the Interface

Once started, the web interface will be available at:
- **URL**: http://localhost:8000
- **Default Port**: 8000 (configurable in config.yaml)

## Testing the Installation

To verify all imports work correctly before starting:

```bash
python3 test_imports.py
```

## CLI Usage

To use the command-line interface:

```bash
# Activate venv first
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Run CLI commands
python3 cli.py --help
python3 cli.py devices
python3 cli.py status
```

## Troubleshooting

### ModuleNotFoundError

If you see import errors:
1. Make sure PYTHONPATH is set: `export PYTHONPATH="${PWD}:${PYTHONPATH}"`
2. Verify virtual environment is activated: `source venv/bin/activate`
3. Run the test script: `python3 test_imports.py`

### Missing Dependencies

If dependencies are missing:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Config File Not Found

Make sure `config.yaml` exists in the project root directory.

## What's Been Fixed

The following import issues have been resolved:
1. All imports now use absolute imports with `src.` prefix
2. PYTHONPATH is properly configured
3. requirements.txt updated with PyYAML and Pydantic
4. Start script created for easy launching

## Next Steps

1. Start the web interface using `./start_demo.sh`
2. Navigate to http://localhost:8000
3. Check the status page to verify engines are loaded
4. Try recording or transcribing audio
