#!/usr/bin/env python3
"""
Test script to demonstrate debug logging
Shows all log levels and error handling
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

# Create logs directory
Path("debug/logs").mkdir(parents=True, exist_ok=True)

# Configure logging
log_format = '[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Setup handlers
debug_log = f"debug/logs/test_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
error_log = f"debug/logs/test_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

file_handler = logging.FileHandler(debug_log)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

error_handler = logging.FileHandler(error_log)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(log_format, date_format))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console_handler, file_handler, error_handler]
)

logger = logging.getLogger(__name__)

def test_all_log_levels():
    """Demonstrate all log levels"""
    print("\n" + "="*65)
    print("TESTING ALL LOG LEVELS")
    print("="*65 + "\n")

    logger.debug("This is a DEBUG message - detailed diagnostic info")
    logger.info("This is an INFO message - general information")
    logger.warning("This is a WARNING message - something unexpected")
    logger.error("This is an ERROR message - something failed")
    logger.critical("This is a CRITICAL message - serious problem")

def test_hardware_detection():
    """Test hardware detection with logging"""
    print("\n" + "="*65)
    print("TESTING HARDWARE DETECTION")
    print("="*65 + "\n")

    try:
        logger.info("Starting hardware detection...")
        from src.utils.hardware import get_hardware_detector

        logger.debug("Importing hardware detector module")
        hw = get_hardware_detector()

        logger.info("Hardware detector initialized successfully")
        info = hw.get_system_info()

        logger.debug(f"Architecture: {info['architecture']}")
        logger.debug(f"SoC Type: {info['soc_type']}")
        logger.debug(f"CPU Count: {info['cpu_info']['cpu_count']}")

        if info['npu_info']['available']:
            logger.info(f"NPU detected: {info['npu_info']['description']}")
            logger.debug(f"NPU TOPS: {info['npu_info']['tops']}")
        else:
            logger.warning("No NPU detected on this system")

        logger.info("Hardware detection completed successfully")
        return True

    except Exception as e:
        logger.error(f"Hardware detection failed: {e}")
        logger.debug("Stack trace:", exc_info=True)
        return False

def test_error_handling():
    """Test error handling and logging"""
    print("\n" + "="*65)
    print("TESTING ERROR HANDLING")
    print("="*65 + "\n")

    logger.info("Testing error handling...")

    # Test 1: File not found
    try:
        logger.debug("Attempting to read non-existent file")
        with open("nonexistent_file.txt", 'r') as f:
            data = f.read()
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.debug("This is expected - demonstrating error logging")

    # Test 2: Import error
    try:
        logger.debug("Attempting to import non-existent module")
        import nonexistent_module
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.debug("This is expected - demonstrating import error logging")

    # Test 3: Division by zero
    try:
        logger.debug("Attempting division by zero")
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Math error: {e}")
        logger.debug("This is expected - demonstrating exception logging")

    logger.info("Error handling test completed")

def test_performance_logging():
    """Test performance logging"""
    print("\n" + "="*65)
    print("TESTING PERFORMANCE LOGGING")
    print("="*65 + "\n")

    import time

    logger.info("Starting performance test...")

    # Simulate some work
    operations = [
        ("Loading model", 0.5),
        ("Processing audio", 1.0),
        ("Transcribing", 2.0),
        ("Generating summary", 1.5)
    ]

    for operation, duration in operations:
        logger.debug(f"Starting: {operation}")
        start_time = time.time()

        # Simulate work
        time.sleep(duration)

        elapsed = time.time() - start_time
        logger.info(f"{operation} took {elapsed:.2f}s")

    logger.info("Performance test completed")

def main():
    """Main test function"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         Debug Logging Test                                    ║
║         Demonstrates all logging features                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    print(f"\n📝 Debug log:  {debug_log}")
    print(f"❌ Error log:  {error_log}\n")

    # Run tests
    test_all_log_levels()
    test_hardware_detection()
    test_error_handling()
    test_performance_logging()

    # Summary
    print("\n" + "="*65)
    print("TEST SUMMARY")
    print("="*65)
    print(f"\n✅ All tests completed!")
    print(f"\n📄 Log files created:")
    print(f"   • Debug log (all levels): {debug_log}")
    print(f"   • Error log (errors only): {error_log}")
    print(f"\n💡 View logs:")
    print(f"   cat {debug_log}")
    print(f"   cat {error_log}")
    print(f"\n📊 Log statistics:")

    # Count log levels in debug log
    with open(debug_log, 'r') as f:
        content = f.read()
        print(f"   DEBUG messages:    {content.count('DEBUG')}")
        print(f"   INFO messages:     {content.count('INFO')}")
        print(f"   WARNING messages:  {content.count('WARNING')}")
        print(f"   ERROR messages:    {content.count('ERROR')}")
        print(f"   CRITICAL messages: {content.count('CRITICAL')}")

    print()

if __name__ == "__main__":
    main()
