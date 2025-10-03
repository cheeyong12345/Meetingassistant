#!/usr/bin/env python3
"""
RISC-V Installation Fix Script
Automatically fixes SciPy/gfortran installation issues on RISC-V
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_banner():
    """Print script banner"""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         RISC-V Installation Fix Script                       ║
║         Fixes SciPy/gfortran Issues                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{Colors.NC}
    """
    print(banner)

def print_status(message: str):
    print(f"{Colors.GREEN}[✓]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[!]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[✗]{Colors.NC} {message}")

def print_info(message: str):
    print(f"{Colors.BLUE}[i]{Colors.NC} {message}")

def run_command(cmd, check=True, shell=False, timeout=None):
    """Run a command and return result"""
    try:
        if shell:
            result = subprocess.run(
                cmd,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        else:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=True,
                text=True,
                timeout=timeout
            )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
            print_error(f"Error: {e.stderr}")
            raise
        return e
    except subprocess.TimeoutExpired:
        print_error("Command timed out")
        raise

def check_architecture():
    """Check if running on RISC-V"""
    print_info("Checking system architecture...")
    arch = platform.machine().lower()
    print_info(f"Architecture: {arch}")

    if arch in ["riscv64", "riscv"]:
        print_status("RISC-V architecture detected")
        return True
    else:
        print_warning(f"Not RISC-V architecture (detected: {arch})")
        response = input("Continue anyway? (y/N): ").strip().lower()
        return response in ['y', 'yes']

def check_sudo():
    """Check if user has sudo privileges"""
    print_info("Checking sudo privileges...")
    result = run_command(["sudo", "-n", "true"], check=False)

    if result.returncode != 0:
        print_warning("This script needs sudo privileges to install system packages")
        print_info("You may be prompted for your password")
        result = run_command(["sudo", "true"])

    print_status("Sudo access confirmed")
    return True

def check_package_installed(package):
    """Check if a system package is installed"""
    result = run_command(["dpkg", "-l", package], check=False)
    return result.returncode == 0

def install_system_packages():
    """Install required system packages"""
    print_info("\n" + "="*60)
    print_info("STEP 1: Installing System Packages")
    print_info("="*60)

    packages = [
        ("gfortran", "Fortran compiler (required for SciPy)"),
        ("libopenblas-dev", "Optimized BLAS library"),
        ("liblapack-dev", "Linear Algebra library"),
        ("libblas-dev", "Basic Linear Algebra library"),
        ("python3-dev", "Python development headers"),
        ("build-essential", "Build tools (gcc, make, etc.)")
    ]

    # Check which packages need to be installed
    to_install = []
    for package, description in packages:
        if check_package_installed(package):
            print_status(f"{package:20s} already installed")
        else:
            print_warning(f"{package:20s} not installed - will install")
            to_install.append(package)

    if not to_install:
        print_status("All required packages already installed")
        return True

    # Update package list
    print_info("\nUpdating package list...")
    run_command(["sudo", "apt", "update"])
    print_status("Package list updated")

    # Install missing packages
    print_info(f"\nInstalling {len(to_install)} packages...")
    for pkg in to_install:
        print_info(f"  - {pkg}")

    result = run_command(["sudo", "apt", "install", "-y"] + to_install)

    if result.returncode == 0:
        print_status("System packages installed successfully")
        return True
    else:
        print_error("Failed to install system packages")
        return False

def check_venv():
    """Check if virtual environment exists and is activated"""
    print_info("\n" + "="*60)
    print_info("STEP 2: Checking Virtual Environment")
    print_info("="*60)

    # Check if we're in a venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print_status("Virtual environment is active")
        print_info(f"Python: {sys.executable}")
        return True
    else:
        print_warning("Not running in a virtual environment")

        # Check if venv exists
        venv_path = Path("venv")
        if venv_path.exists():
            print_info("Found virtual environment at: venv/")
            print_info("Please activate it first:")
            print_info("  source venv/bin/activate")
            print_info("  python3 scripts/fix_riscv_install.py")
            return False
        else:
            print_warning("No virtual environment found")
            response = input("Create virtual environment now? (Y/n): ").strip().lower()

            if response in ['', 'y', 'yes']:
                print_info("Creating virtual environment...")
                run_command(["python3", "-m", "venv", "venv"])
                print_status("Virtual environment created")
                print_info("Please activate it and re-run this script:")
                print_info("  source venv/bin/activate")
                print_info("  python3 scripts/fix_riscv_install.py")
                return False
            else:
                print_warning("Skipping virtual environment - will install to system Python")
                return True

def get_pip_path():
    """Get pip path (venv or system)"""
    # Check if in venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        return str(Path(sys.executable).parent / "pip")
    else:
        return "pip3"

def check_python_package(package):
    """Check if a Python package is installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_numpy():
    """Install NumPy"""
    print_info("\n" + "="*60)
    print_info("STEP 3: Installing NumPy")
    print_info("="*60)

    if check_python_package("numpy"):
        import numpy
        print_status(f"NumPy already installed: {numpy.__version__}")
        return True

    print_info("Installing NumPy (may take 5-10 minutes on RISC-V)...")
    print_info("This is being compiled from source - please be patient")

    pip_path = get_pip_path()

    try:
        result = run_command([pip_path, "install", "numpy"], timeout=1800)  # 30 min timeout

        if result.returncode == 0:
            import numpy
            print_status(f"NumPy installed successfully: {numpy.__version__}")
            return True
        else:
            print_error("NumPy installation failed")
            return False

    except subprocess.TimeoutExpired:
        print_error("NumPy installation timed out (>30 minutes)")
        return False

def install_scipy():
    """Install SciPy"""
    print_info("\n" + "="*60)
    print_info("STEP 4: Installing SciPy")
    print_info("="*60)

    if check_python_package("scipy"):
        import scipy
        print_status(f"SciPy already installed: {scipy.__version__}")
        return True

    print_warning("SciPy installation on RISC-V takes 10-30 minutes")
    print_info("The build is compiling Fortran code - this is normal")

    response = input("\nProceed with SciPy installation? (Y/n/skip): ").strip().lower()

    if response in ['n', 'no']:
        print_warning("Skipping SciPy installation")
        print_info("Note: Core functionality works without SciPy")
        return True

    if response == 'skip':
        print_info("Skipping SciPy - will continue without it")
        return True

    print_info("Installing SciPy...")
    print_info("⏰ This will take 10-30 minutes - grab a coffee! ☕")

    pip_path = get_pip_path()
    start_time = time.time()

    try:
        result = run_command([pip_path, "install", "scipy", "--verbose"], timeout=3600)  # 60 min timeout

        elapsed = time.time() - start_time
        minutes = int(elapsed / 60)

        if result.returncode == 0:
            import scipy
            print_status(f"SciPy installed successfully: {scipy.__version__}")
            print_info(f"Installation took {minutes} minutes")
            return True
        else:
            print_error("SciPy installation failed")
            print_warning("Continuing without SciPy - core features will still work")
            return True  # Don't fail completely

    except subprocess.TimeoutExpired:
        print_error("SciPy installation timed out (>60 minutes)")
        print_warning("This is unusual - there may be a build issue")
        print_warning("Continuing without SciPy")
        return True  # Don't fail completely

def install_other_packages():
    """Install other critical packages"""
    print_info("\n" + "="*60)
    print_info("STEP 5: Installing Other Dependencies")
    print_info("="*60)

    pip_path = get_pip_path()

    packages = {
        'onnxruntime': 'ONNX Runtime (for NPU acceleration)',
        'transformers': 'Hugging Face Transformers',
        'fastapi': 'FastAPI web framework',
        'pyaudio': 'Audio processing'
    }

    for package, description in packages.items():
        if check_python_package(package):
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print_status(f"{package:20s} already installed ({version})")
        else:
            print_info(f"Installing {package} ({description})...")
            result = run_command([pip_path, "install", package], check=False, timeout=600)

            if result.returncode == 0:
                print_status(f"{package:20s} installed")
            else:
                print_warning(f"{package:20s} installation failed (optional)")

    return True

def verify_installation():
    """Verify the installation"""
    print_info("\n" + "="*60)
    print_info("STEP 6: Verification")
    print_info("="*60)

    critical_packages = ['numpy', 'onnxruntime', 'transformers', 'fastapi']
    optional_packages = ['scipy', 'torch']

    print_info("\nCritical packages:")
    all_critical_ok = True
    for package in critical_packages:
        if check_python_package(package):
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print_status(f"  ✓ {package:20s} {version}")
        else:
            print_error(f"  ✗ {package:20s} NOT INSTALLED")
            all_critical_ok = False

    print_info("\nOptional packages:")
    for package in optional_packages:
        if check_python_package(package):
            mod = __import__(package)
            version = getattr(mod, '__version__', 'unknown')
            print_status(f"  ✓ {package:20s} {version}")
        else:
            print_warning(f"  - {package:20s} not installed (optional)")

    return all_critical_ok

def print_summary():
    """Print summary and next steps"""
    print_info("\n" + "="*60)
    print_info("INSTALLATION COMPLETE")
    print_info("="*60)

    print_status("\n✅ RISC-V installation fix completed!")

    print_info("\n📋 Next Steps:")
    print_info("  1. Continue with model installation:")
    print_info("     python3 scripts/install_sbc.py --models-only")
    print_info("")
    print_info("  2. Test the installation:")
    print_info("     python3 -c 'import numpy; print(\"NumPy:\", numpy.__version__)'")
    print_info("     python3 -c 'import onnxruntime; print(\"ONNX:\", onnxruntime.__version__)'")
    print_info("")
    print_info("  3. Run the web app:")
    print_info("     python3 web_app.py")
    print_info("")
    print_info("  4. Or run in debug mode:")
    print_info("     python3 debug/run_debug.py")

    print_info("\n📚 Documentation:")
    print_info("  - RISCV_INSTALL_FIX.md - Troubleshooting guide")
    print_info("  - docs/RISCV_DEPLOYMENT.md - Complete RISC-V guide")
    print_info("  - debug/README_DEBUG.md - Debug mode guide")

def main():
    """Main function"""
    print_banner()

    try:
        # Check architecture
        if not check_architecture():
            print_error("Aborting installation")
            sys.exit(1)

        # Check sudo
        if not check_sudo():
            print_error("Cannot proceed without sudo access")
            sys.exit(1)

        # Install system packages
        if not install_system_packages():
            print_error("Failed to install system packages")
            sys.exit(1)

        # Check virtual environment
        if not check_venv():
            print_info("\nPlease activate virtual environment and re-run this script")
            sys.exit(0)

        # Install Python packages
        if not install_numpy():
            print_error("NumPy installation failed - cannot continue")
            sys.exit(1)

        install_scipy()  # Optional, won't fail if it doesn't work

        install_other_packages()

        # Verify
        if not verify_installation():
            print_warning("\nSome critical packages are missing")
            print_info("Try running: pip install numpy onnxruntime transformers fastapi")
            sys.exit(1)

        # Summary
        print_summary()

    except KeyboardInterrupt:
        print_error("\n\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
