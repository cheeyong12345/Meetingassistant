#!/usr/bin/env python3
"""
Debug Mode Launcher for Meeting Assistant
Runs the application with verbose logging and debug features enabled
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
    "debug/data/meetings",
    "debug/profiles"
]

for dir_path in debug_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# Configure logging
log_format = '[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Console handler - show everything
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# File handler - debug log
debug_log_file = f"debug/logs/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(debug_log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Error handler - errors only
error_log_file = f"debug/logs/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
error_handler = logging.FileHandler(error_log_file)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler, error_handler]
)

logger = logging.getLogger(__name__)

# Suppress some verbose third-party loggers (optional)
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

def print_banner():
    """Print debug mode banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         Meeting Assistant - DEBUG MODE                        ║
║                                                               ║
║  All logging enabled • Verbose output • Debug features        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print(f"\n📝 Debug log:  {debug_log_file}")
    print(f"❌ Error log:  {error_log_file}")
    print(f"📁 Debug data: debug/\n")
    print("="*65)
    logger.info("Debug mode activated - all logging enabled")

def print_system_info():
    """Print detailed system information"""
    logger.info("="*65)
    logger.info("SYSTEM INFORMATION")
    logger.info("="*65)

    import platform
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Architecture: {platform.machine()}")
    logger.info(f"Processor: {platform.processor()}")

    # Check hardware detection
    try:
        from src.utils.hardware import get_hardware_detector
        hw = get_hardware_detector()
        info = hw.get_system_info()

        logger.info(f"SoC Type: {info['soc_type']}")
        logger.info(f"CPU Count: {info['cpu_info']['cpu_count']}")

        if info['npu_info']['available']:
            logger.info(f"NPU: {info['npu_info']['description']}")
            logger.info(f"NPU TOPS: {info['npu_info']['tops']}")
        else:
            logger.info("NPU: Not available")

    except Exception as e:
        logger.error(f"Error getting hardware info: {e}")
        logger.debug(traceback.format_exc())

    logger.info("="*65)

def check_dependencies():
    """Check and log all dependencies"""
    logger.info("="*65)
    logger.info("DEPENDENCY CHECK")
    logger.info("="*65)

    dependencies = {
        'numpy': 'NumPy',
        'torch': 'PyTorch',
        'whisper': 'OpenAI Whisper',
        'transformers': 'Hugging Face Transformers',
        'onnxruntime': 'ONNX Runtime',
        'pyaudio': 'PyAudio',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn'
    }

    for module, name in dependencies.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            logger.info(f"✅ {name:30s} {version}")
        except ImportError:
            logger.warning(f"❌ {name:30s} NOT INSTALLED")

    logger.info("="*65)

def main():
    """Main debug runner"""
    print_banner()

    try:
        logger.info("Starting Meeting Assistant in DEBUG mode")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Config file: debug/config_debug.yaml")

        # Print system info
        print_system_info()

        # Check dependencies
        check_dependencies()

        # Import and run web app
        logger.info("Importing web application...")

        # Change to parent directory for imports
        os.chdir(parent_dir)

        from web_app import app
        import uvicorn

        logger.info("Starting FastAPI server in debug mode...")
        logger.info("Access the application at: http://localhost:8001")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*65)

        # Run with debug configuration
        uvicorn.run(
            app,
            host="localhost",
            port=8001,
            log_level="debug",
            reload=True,
            reload_dirs=[str(parent_dir / "src"), str(parent_dir / "web_app.py")]
        )

    except KeyboardInterrupt:
        logger.info("\n\nShutting down debug mode...")
        logger.info(f"Logs saved to:")
        logger.info(f"  - {debug_log_file}")
        logger.info(f"  - {error_log_file}")

    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
