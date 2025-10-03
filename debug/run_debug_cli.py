#!/usr/bin/env python3
"""
Debug Mode CLI Launcher for Meeting Assistant
Runs the CLI with verbose logging and debug features enabled
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

# Create debug directories
debug_dirs = [
    "debug/logs",
    "debug/audio",
    "debug/audio_chunks",
    "debug/stt_results",
    "debug/summaries",
    "debug/data",
    "debug/data/meetings"
]

for dir_path in debug_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# Configure logging
log_format = '[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# File handler - debug log
debug_log_file = f"debug/logs/cli_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(debug_log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Error handler
error_log_file = f"debug/logs/cli_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
error_handler = logging.FileHandler(error_log_file)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))

# Console handler - INFO and above for cleaner CLI output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler, error_handler]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print debug CLI banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         Meeting Assistant CLI - DEBUG MODE                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"📝 Debug log:  {debug_log_file}")
    print(f"❌ Error log:  {error_log_file}\n")
    logger.info("CLI Debug mode activated")

def main():
    """Main debug CLI runner"""
    print_banner()

    try:
        os.chdir(parent_dir)

        # Set config to debug version
        os.environ['CONFIG_FILE'] = 'debug/config_debug.yaml'

        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Config file: debug/config_debug.yaml")
        logger.info(f"Arguments: {sys.argv[1:]}")

        # Import and run CLI
        import cli

    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
