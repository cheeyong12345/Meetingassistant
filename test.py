#!/usr/bin/env python3
"""
Meeting Assistant Test Runner
Convenient test runner for Meeting Assistant with multiple test options
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Meeting Assistant Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Types:
  quick      Fast system check and component verification
  setup      Audio devices and engine detection
  complete   Full functionality test with audio download
  all        Run all tests in sequence

Examples:
  python3 test.py quick              # Quick system check
  python3 test.py setup              # Test audio and engines
  python3 test.py complete           # Full functionality test
  python3 test.py all                # Run all tests
  python3 test.py quick --verbose    # Verbose output
  python3 test.py all --continue     # Continue on failures

Test Descriptions:
  - Quick Test: Verifies imports, file structure, and basic components
  - Setup Test: Tests microphone devices and engine initialization
  - Complete Test: Downloads audio, tests transcription and summarization
  - All Tests: Runs quick, setup, and complete tests in sequence

Exit Codes:
  0 - All tests passed
  1 - One or more tests failed
  2 - Invalid arguments or missing files
        """)

    parser.add_argument('test_type',
                       choices=['quick', 'setup', 'complete', 'all'],
                       help='Type of test to run')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    parser.add_argument('--continue-on-failure', '-c', action='store_true',
                       help='Continue running tests even if one fails')

    parser.add_argument('--venv-path',
                       help='Custom path to virtual environment')

    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout for individual tests in seconds (default: 300)')

    return parser.parse_args()

def print_header():
    """Print test runner header"""
    print("🎯 Meeting Assistant Test Runner")
    print("=================================")
    print()

def run_test_script(script_name: str, description: str, args) -> bool:
    """Run a test script"""
    script_dir = Path(__file__).parent.absolute()

    # Determine virtual environment path
    if args.venv_path:
        venv_python = Path(args.venv_path) / "bin" / "python3"
    else:
        venv_python = script_dir / "venv" / "bin" / "python3"

    if not venv_python.exists():
        print("Error: Virtual environment not found.")
        print("Please run an installation script first:")
        print("  python3 install_sbc.py         - Full installation")
        print("  python3 install_lightweight.py - Lightweight installation")
        return False

    script_path = script_dir / script_name
    if not script_path.exists():
        # Try in tests directory
        script_path = script_dir / "tests" / script_name
        if not script_path.exists():
            print(f"Error: Test script {script_name} not found.")
            return False

    print(f"🚀 Running {description}...")
    if args.verbose:
        print(f"   Script: {script_path}")
        print(f"   Python: {venv_python}")
        print(f"   Timeout: {args.timeout}s")

    try:
        result = subprocess.run(
            [str(venv_python), str(script_path)],
            check=True,
            timeout=args.timeout,
            capture_output=not args.verbose,
            text=True
        )

        if args.verbose and result.stdout:
            print(result.stdout)

        print(f"✅ {description} completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code: {e.returncode}")
        if args.verbose and e.stderr:
            print(f"Error output: {e.stderr}")
        return False

    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} timed out after {args.timeout} seconds")
        return False

    except KeyboardInterrupt:
        print(f"\n⏹️  {description} interrupted by user")
        return False

def main():
    """Main test runner function"""
    try:
        args = parse_arguments()
    except SystemExit:
        return

    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    print_header()

    if args.verbose:
        print(f"Test type: {args.test_type}")
        print(f"Working directory: {script_dir}")
        print(f"Continue on failure: {args.continue_on_failure}")
        print()

    success = True

    if args.test_type == "quick":
        success = run_test_script("quick_test.py", "Quick Test", args)

    elif args.test_type == "setup":
        success = run_test_script("test_setup.py", "Setup Test", args)

    elif args.test_type == "complete":
        success = run_test_script("run_complete_test.py", "Complete Test", args)

    elif args.test_type == "all":
        print("🚀 Running All Tests...")
        print()

        # Run tests in sequence
        tests = [
            ("quick_test.py", "Quick Test"),
            ("test_setup.py", "Setup Test"),
            ("run_complete_test.py", "Complete Test")
        ]

        all_passed = True
        for script, description in tests:
            test_passed = run_test_script(script, description, args)
            if not test_passed:
                all_passed = False
                if not args.continue_on_failure:
                    print(f"\n❌ Stopping tests due to failure in {description}")
                    break
            print()  # Add spacing between tests

        if all_passed:
            print("🎉 All tests completed successfully!")
        else:
            print("❌ Some tests failed. Check output above for details.")

        success = all_passed

    # Print final summary
    print()
    print("=" * 50)
    if success:
        print("✅ TEST SUITE PASSED")
        print()
        print("Your Meeting Assistant installation is working correctly!")
        print("You can now:")
        print("  python3 run_cli.py      # Use CLI interface")
        print("  python3 run_web.py      # Use web interface")
    else:
        print("❌ TEST SUITE FAILED")
        print()
        print("Some issues were detected. Common solutions:")
        print("  - Re-run installation: python3 install_sbc.py")
        print("  - Check dependencies: pip install -r requirements.txt")
        print("  - Check microphone permissions")
        print("  - Verify audio device connections")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()