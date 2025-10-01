#!/usr/bin/env python3
"""
Meeting Assistant Lightweight Installation Script
Minimal installation with essential features only
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
from pathlib import Path
from typing import List

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_status(message: str):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header(message: str):
    print(f"{Colors.BLUE}=== {message} ==={Colors.NC}")

def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {' '.join(cmd)}")
            print_error(f"Error: {e.stderr}")
            raise
        return e

def command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH"""
    return shutil.which(cmd) is not None

def check_dependencies() -> bool:
    """Check for required system dependencies"""
    print_header("Checking System Dependencies")

    missing_deps = []
    required_commands = ["python3", "pip3"]

    for cmd in required_commands:
        if command_exists(cmd):
            print_status(f"{cmd} is available")
        else:
            missing_deps.append(cmd)

    # Check Python version
    if command_exists("python3"):
        result = run_command(["python3", "--version"])
        python_version = result.stdout.split()[1]
        print_status(f"Python version: {python_version}")

        # Check if Python version is >= 3.8
        version_check = run_command([
            "python3", "-c",
            "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
        ], check=False)

        if version_check.returncode == 0:
            print_status("Python version is compatible")
        else:
            print_error("Python 3.8 or higher is required")
            return False

    if missing_deps:
        print_error(f"Missing dependencies: {', '.join(missing_deps)}")
        print_status(f"Please install: sudo apt update && sudo apt install -y {' '.join(missing_deps)}")
        return False

    return True

def install_minimal_packages() -> bool:
    """Install minimal system packages"""
    print_header("Installing Minimal Packages")

    packages = [
        "python3-dev", "python3-pip", "python3-venv",
        "portaudio19-dev", "git"
    ]

    print_status(f"Installing packages: {', '.join(packages)}")
    run_command(["sudo", "apt", "update"])
    run_command(["sudo", "apt", "install", "-y"] + packages)

    return True

def setup_python_env() -> bool:
    """Setup Python virtual environment"""
    print_header("Setting up Python Environment")

    venv_path = Path("venv")
    if not venv_path.exists():
        print_status("Creating Python virtual environment")
        run_command(["python3", "-m", "venv", "venv"])
    else:
        print_status("Virtual environment already exists")

    # Activate virtual environment and upgrade pip
    pip_path = venv_path / "bin" / "pip"
    print_status("Upgrading pip")
    run_command([str(pip_path), "install", "--upgrade", "pip"])

    return True

def install_minimal_deps() -> bool:
    """Install minimal Python dependencies"""
    print_header("Installing Minimal Dependencies")

    pip_path = Path("venv/bin/pip")

    print_status("Installing core dependencies")
    run_command([str(pip_path), "install", "numpy", "pyyaml", "click", "rich"])

    print_status("Installing audio dependencies")
    run_command([str(pip_path), "install", "pyaudio", "pydub"])

    print_status("Installing web framework")
    run_command([str(pip_path), "install", "fastapi", "uvicorn", "jinja2", "python-multipart", "aiofiles"])

    print_status("Installing basic STT")
    run_command([str(pip_path), "install", "SpeechRecognition"])

    print_status("Installing utilities")
    run_command([str(pip_path), "install", "python-dotenv", "requests", "sqlalchemy"])

    return True

def create_minimal_config():
    """Create minimal configuration"""
    print_header("Creating Minimal Configuration")

    config_content = '''# Meeting Assistant Minimal Configuration
app:
  name: "Meeting Assistant"
  version: "1.0.0"
  debug: false

# Server configuration
server:
  host: "localhost"
  port: 8000
  reload: true

# Audio settings
audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024
  format: "wav"
  input_device: null

# Speech-to-Text (minimal)
stt:
  default_engine: "google"
  engines:
    google:
      api_key: null
      language: "en-US"

# Summarization (API-based only)
summarization:
  default_engine: "openai"
  engines:
    openai:
      api_key: null
      model: "gpt-3.5-turbo"
      max_tokens: 1000

# Storage settings
storage:
  data_dir: "./data"
  meetings_dir: "./data/meetings"
  models_dir: "./models"
  database_url: "sqlite:///./data/meetings.db"

# Processing settings
processing:
  real_time_stt: false
  auto_summarize: false
  speaker_detection: false
  chunk_duration: 30
  max_meeting_duration: 14400
'''

    with open("config.yaml", 'w') as f:
        f.write(config_content)

    print_status("Minimal configuration created")

def create_scripts():
    """Create startup scripts"""
    print_header("Creating Startup Scripts")

    # Create minimal CLI launcher script
    with open("run_cli_minimal.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

print("Meeting Assistant - Minimal Mode")
print("Note: This installation requires API keys for STT and summarization")

# Activate virtual environment
venv_python = script_dir / "venv" / "bin" / "python3"
if not venv_python.exists():
    print("Error: Virtual environment not found. Please run install_lightweight.py first.")
    sys.exit(1)

# Run CLI with arguments
cmd = [str(venv_python), "cli.py"] + sys.argv[1:]
subprocess.run(cmd)
''')

    # Create minimal web launcher script
    with open("run_web_minimal.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)

print("Meeting Assistant Web - Minimal Mode")
print("Configure API keys in config.yaml before use")

# Activate virtual environment
venv_python = script_dir / "venv" / "bin" / "python3"
if not venv_python.exists():
    print("Error: Virtual environment not found. Please run install_lightweight.py first.")
    sys.exit(1)

# Run web app
subprocess.run([str(venv_python), "web_app.py"])
''')

    # Make scripts executable
    for script in ["run_cli_minimal.py", "run_web_minimal.py"]:
        os.chmod(script, 0o755)

    print_status("Created minimal launcher scripts")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Meeting Assistant Lightweight Installation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install_lightweight.py                # Interactive installation
  python3 install_lightweight.py --auto-confirm # Skip confirmation prompts
  python3 install_lightweight.py --config-only  # Only create configuration
  python3 install_lightweight.py --test-only    # Only run tests

Features Installed:
  - Basic audio recording (PyAudio)
  - Web interface (FastAPI)
  - CLI interface (Click)
  - API-based STT (Google Speech)
  - API-based summarization (OpenAI)

Requirements:
  - Internet connection
  - API keys for Google Speech and OpenAI
  - ~50MB storage space

Note: This is a minimal installation without local AI models.
For full offline functionality, use install_sbc.py instead.
        """)

    parser.add_argument('--auto-confirm', '-y', action='store_true',
                       help='Skip confirmation prompts')

    parser.add_argument('--config-only', action='store_true',
                       help='Only create configuration files')

    parser.add_argument('--test-only', action='store_true',
                       help='Only run installation tests')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    return parser.parse_args()

def main():
    """Main installation function"""
    args = parse_arguments()

    print_header("Meeting Assistant Lightweight Installation")

    print("==========================================")
    print("Meeting Assistant Lightweight Installation")
    print("==========================================")

    # Check if running as root
    if os.geteuid() == 0:
        print_error("Please don't run this script as root")
        sys.exit(1)

    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    if args.test_only:
        print_status("Running lightweight installation tests...")
        # Test basic functionality
        try:
            import yaml, click, requests
            print_status("Basic dependencies available")
        except ImportError as e:
            print_error(f"Missing dependencies: {e}")
            sys.exit(1)
        return

    if not args.config_only:
        print()
        print_status("This is a lightweight installation that includes:")
        print("  ✓ Basic audio recording")
        print("  ✓ Web interface")
        print("  ✓ CLI interface")
        print("  ✓ API-based STT (Google Speech)")
        print("  ✓ API-based summarization (OpenAI)")
        print()
        print_warning("This installation does NOT include:")
        print("  ✗ Local AI models (Whisper, Qwen)")
        print("  ✗ Offline processing")
        print("  ✗ Large model downloads")
        print()
        print_status("Total download size: ~50MB (vs ~2-7GB for full installation)")
        print()

        if not args.auto_confirm:
            response = input("Continue with lightweight installation? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print_status("Installation cancelled")
                sys.exit(0)

    try:
        if not args.config_only:
            if not check_dependencies():
                sys.exit(1)

            install_minimal_packages()
            setup_python_env()
            install_minimal_deps()

        create_minimal_config()
        create_scripts()

        print_header("Lightweight Installation Complete!")
        print(f"{Colors.GREEN}Installation completed successfully!{Colors.NC}")
        print()
        print("Next steps:")
        print("1. Configure API keys in config.yaml:")
        print("   - Google Speech API key for STT")
        print("   - OpenAI API key for summarization")
        print("2. Test: python3 run_cli_minimal.py test")
        print("3. Run web: python3 run_web_minimal.py")
        print()
        print(f"{Colors.YELLOW}Note: This minimal installation requires internet and API keys{Colors.NC}")
        print(f"{Colors.BLUE}For full offline functionality, run python3 install_sbc.py instead{Colors.NC}")

    except KeyboardInterrupt:
        print_error("\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()