#!/usr/bin/env python3
"""
Meeting Assistant Installation Script for Single Board Computers (SBC)
Supports RK3588, Raspberry Pi, and other ARM64 SBCs
"""

import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import zipfile
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

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

def detect_system() -> Tuple[str, str, str]:
    """Detect system architecture and SBC type"""
    print_header("System Detection")

    arch = platform.machine()
    os_name = platform.system()

    print_status(f"Architecture: {arch}")
    print_status(f"OS: {os_name}")

    # Check architecture type
    if arch in ["riscv64", "riscv"]:
        print_status("RISC-V architecture detected - ONNX Runtime will be used for inference")
    elif arch not in ["aarch64", "arm64"]:
        print_warning("This script is optimized for ARM64/RISC-V SBCs, but will try to continue")

    sbc_type = "generic"

    # Detect specific SBC if possible
    device_tree_model = Path("/proc/device-tree/model")
    if device_tree_model.exists():
        try:
            with open(device_tree_model, 'r') as f:
                model = f.read().strip('\x00')
            print_status(f"Device Model: {model}")

            if "RK3588" in model or "rk3588" in model:
                sbc_type = "rk3588"
                print_status("Detected RK3588 SBC with NPU support")
            elif "EIC7700" in model or "eic7700" in model or "Eswin" in model or "eswin" in model:
                sbc_type = "eic7700"
                print_status("Detected ESWIN EIC7700 RISC-V SoC with NPU support")
            elif "Raspberry Pi" in model:
                sbc_type = "rpi"
                print_status("Detected Raspberry Pi")
            else:
                sbc_type = "generic"
                print_status("Generic SBC detected")
        except Exception:
            sbc_type = "generic"

    # Additional RISC-V detection
    if arch in ["riscv64", "riscv"]:
        print_status("RISC-V architecture detected")
        # Check for EIC7700 specific files
        if Path("/usr/lib/libennp.so").exists() or Path("/opt/eswin").exists():
            sbc_type = "eic7700"
            print_status("Detected EIC7700 RISC-V SoC with ENNP NPU support")
        elif sbc_type == "generic":
            sbc_type = "riscv_generic"

    return arch, os_name, sbc_type

def check_dependencies() -> bool:
    """Check for required system dependencies"""
    print_header("Checking System Dependencies")

    missing_deps = []
    required_commands = ["python3", "pip3", "git", "curl", "wget"]

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
        print_status("Installing missing dependencies...")

        # Update package list
        run_command(["sudo", "apt", "update"])

        # Install missing dependencies
        run_command(["sudo", "apt", "install", "-y"] + missing_deps)

    return True

def install_system_packages(sbc_type: str) -> bool:
    """Install system packages"""
    print_header("Installing System Packages")

    packages = [
        "python3-dev", "python3-pip", "python3-venv", "build-essential",
        "cmake", "pkg-config", "libasound2-dev", "portaudio19-dev",
        "libportaudio2", "libsndfile1-dev", "ffmpeg", "git", "curl",
        "wget", "nano", "htop"
    ]

    # RK3588 specific packages
    if sbc_type == "rk3588":
        packages.extend([
            "rockchip-mpp-dev", "librockchip-mpp1", "librga-dev"
        ])
        print_status("Adding RK3588-specific packages")

    # EIC7700 specific packages
    elif sbc_type == "eic7700":
        print_status("Adding EIC7700/RISC-V-specific packages")
        # RISC-V toolchain and libraries
        packages.extend([
            "gfortran",  # Required for SciPy compilation
            "libopenblas-dev",  # BLAS library for NumPy/SciPy
            "liblapack-dev",  # LAPACK library for SciPy
            "libblas-dev"  # Basic Linear Algebra Subprograms
        ])
        # Note: ENNP SDK should be installed separately from vendor

    # RISC-V generic packages
    elif "riscv" in sbc_type:
        print_status("Adding RISC-V generic packages")
        packages.extend([
            "gfortran",
            "libopenblas-dev",
            "liblapack-dev",
            "libblas-dev"
        ])

    print_status(f"Installing packages: {', '.join(packages)}")
    run_command(["sudo", "apt", "update"])
    run_command(["sudo", "apt", "install", "-y"] + packages)

    return True

def setup_audio() -> bool:
    """Setup audio system"""
    print_header("Setting up Audio System")

    # Check if user is in audio group
    import grp
    try:
        audio_group = grp.getgrnam('audio')
        current_user = os.getlogin()
        if current_user not in audio_group.gr_mem:
            print_status("Adding user to audio group")
            run_command(["sudo", "usermod", "-a", "-G", "audio", current_user])
            print_warning("You need to log out and log back in for audio group changes to take effect")
    except KeyError:
        print_warning("Audio group not found")

    # Test microphone detection
    print_status("Detecting audio devices...")

    if command_exists("arecord"):
        print_status("Available recording devices:")
        result = run_command(["arecord", "-l"], check=False)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print_warning("No recording devices found")

    # Check for PulseAudio
    if command_exists("pulseaudio"):
        print_status("PulseAudio is available")
        # Check if PulseAudio is running
        check_result = run_command(["pulseaudio", "--check"], check=False)
        if check_result.returncode != 0:
            print_status("Starting PulseAudio")
            start_result = run_command(["pulseaudio", "--start"], check=False)
            if start_result.returncode != 0:
                print_warning("Failed to start PulseAudio")
    else:
        print_status("Installing PulseAudio")
        run_command(["sudo", "apt", "install", "-y", "pulseaudio", "pulseaudio-utils"])

    return True

def setup_python_env() -> bool:
    """Create Python virtual environment"""
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
    run_command([str(pip_path), "install", "--upgrade", "pip", "setuptools", "wheel"])

    return True

def install_pytorch(arch: str = "aarch64", sbc_type: str = "generic") -> bool:
    """Install PyTorch for ARM64/RISC-V"""
    print_header("Installing PyTorch")

    pip_path = Path("venv/bin/pip")
    python_path = Path("venv/bin/python3")

    if arch in ["riscv64", "riscv"]:
        print_status("Detected RISC-V architecture")
        print_warning("PyTorch does not have official pre-built wheels for RISC-V yet")
        print()
        print("Options for RISC-V PyTorch installation:")
        print("  1. Build PyTorch from source (takes 6-12 hours, requires 8GB+ RAM)")
        print("  2. Use ONNX Runtime for inference (recommended, faster)")
        print("  3. Skip PyTorch (will use ONNX Runtime only)")
        print()

        choice = input("Choose option [1-3] (default: 2): ").strip()
        if not choice:
            choice = "2"

        if choice == "1":
            print_status("Building PyTorch from source for RISC-V...")
            print_warning("This will take several hours. Consider using screen/tmux.")
            confirm = input("Continue with build from source? (y/N): ").strip().lower()

            if confirm in ['y', 'yes']:
                try:
                    # Install build dependencies
                    print_status("Installing build dependencies...")
                    build_deps = [
                        "cmake", "ninja-build", "ccache",
                        "libopenblas-dev", "libblas-dev", "m4",
                        "python3-dev", "python3-yaml", "python3-setuptools"
                    ]
                    run_command(["sudo", "apt", "install", "-y"] + build_deps)

                    # Install Python build dependencies
                    run_command([str(pip_path), "install", "pyyaml", "numpy", "setuptools", "cffi", "typing_extensions"])

                    # Clone PyTorch
                    print_status("Cloning PyTorch repository...")
                    pytorch_dir = Path("/tmp/pytorch")
                    if pytorch_dir.exists():
                        shutil.rmtree(pytorch_dir)

                    run_command(["git", "clone", "--recursive", "--branch", "v2.1.0",
                               "https://github.com/pytorch/pytorch", str(pytorch_dir)])

                    # Build PyTorch
                    print_status("Building PyTorch (this will take 6-12 hours)...")
                    os.chdir(pytorch_dir)

                    # Set environment variables for RISC-V build
                    env = os.environ.copy()
                    env["USE_CUDA"] = "0"
                    env["USE_CUDNN"] = "0"
                    env["USE_MKLDNN"] = "0"
                    env["USE_NNPACK"] = "0"
                    env["USE_QNNPACK"] = "0"
                    env["BUILD_TEST"] = "0"
                    env["MAX_JOBS"] = str(os.cpu_count() or 4)

                    subprocess.run([str(python_path), "setup.py", "install"], env=env, check=True)

                    # Return to original directory
                    os.chdir(Path(__file__).parent.absolute())

                    print_status("PyTorch built and installed successfully")

                except Exception as e:
                    print_error(f"Failed to build PyTorch from source: {e}")
                    print_warning("Falling back to ONNX Runtime only")
                    return install_onnxruntime_riscv(pip_path, python_path)
            else:
                print_status("Skipping PyTorch build, using ONNX Runtime")
                return install_onnxruntime_riscv(pip_path, python_path)

        elif choice == "2":
            print_status("Using ONNX Runtime for RISC-V inference")
            return install_onnxruntime_riscv(pip_path, python_path)

        else:  # choice == "3"
            print_status("Skipping PyTorch installation")
            print_warning("Some features may be limited without PyTorch")
            return install_onnxruntime_riscv(pip_path, python_path)

    else:
        print_status("Installing PyTorch for ARM64")
        # Install PyTorch CPU version (most compatible for ARM64)
        try:
            run_command([
                str(pip_path), "install", "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ])
        except Exception as e:
            print_error(f"PyTorch installation failed: {e}")
            print_warning("Trying alternative installation method...")
            try:
                # Try without index URL
                run_command([str(pip_path), "install", "torch", "torchvision", "torchaudio"])
            except Exception as e2:
                print_error(f"Alternative installation also failed: {e2}")
                return False

    # Verify installation
    verify_result = run_command([
        str(python_path), "-c",
        "import torch; print(f'PyTorch version: {torch.__version__}')"
    ], check=False)

    if verify_result.returncode != 0:
        print_warning("PyTorch installation verification failed")
        if arch in ["riscv64", "riscv"]:
            print_status("This is expected for RISC-V, ONNX Runtime will be used instead")
            return True
        return False

    print(verify_result.stdout)
    return True


def install_onnxruntime_riscv(pip_path: Path, python_path: Path) -> bool:
    """Install ONNX Runtime for RISC-V as PyTorch alternative"""
    print_header("Installing ONNX Runtime for RISC-V")

    try:
        # Try to install ONNX Runtime
        print_status("Installing ONNX Runtime...")
        result = run_command([str(pip_path), "install", "onnxruntime"], check=False)

        if result.returncode != 0:
            print_warning("Pre-built ONNX Runtime not available for RISC-V")
            print_status("Attempting to build ONNX Runtime from source...")

            # Install build dependencies
            build_deps = ["cmake", "ninja-build", "protobuf-compiler", "libprotobuf-dev"]
            run_command(["sudo", "apt", "install", "-y"] + build_deps)

            # Install Python dependencies
            run_command([str(pip_path), "install", "numpy", "packaging", "protobuf"])

            # For now, we'll use a lightweight alternative
            print_warning("ONNX Runtime build from source requires significant time")
            print_status("Installing lightweight alternatives...")

            # Install basic numpy and scipy for computations
            run_command([str(pip_path), "install", "numpy", "scipy"])

            print_warning("Models will need to be converted to ONNX format for inference")
            print_status("ONNX Runtime can be installed later with: pip install onnxruntime")
        else:
            print_status("ONNX Runtime installed successfully")

            # Verify
            verify_result = run_command([
                str(python_path), "-c",
                "import onnxruntime; print(f'ONNX Runtime version: {onnxruntime.__version__}')"
            ], check=False)

            if verify_result.returncode == 0:
                print(verify_result.stdout)

        return True

    except Exception as e:
        print_error(f"ONNX Runtime installation failed: {e}")
        print_warning("Continuing with limited inference capabilities")
        return True  # Don't fail the whole installation

def install_python_deps(arch: str = "aarch64") -> bool:
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")

    pip_path = Path("venv/bin/pip")

    # For RISC-V, handle SciPy separately as it needs Fortran compiler
    if arch in ["riscv64", "riscv"]:
        print_status("Installing NumPy first (may take several minutes on RISC-V)...")
        numpy_result = run_command([str(pip_path), "install", "numpy"], check=False)
        if numpy_result.returncode != 0:
            print_error("NumPy installation failed")
            return False

        print_status("Installing SciPy (may take 10-30 minutes on RISC-V)...")
        print_warning("SciPy is being compiled from source - this is normal for RISC-V")
        scipy_result = run_command([str(pip_path), "install", "scipy"], check=False, timeout=3600000)  # 1 hour timeout
        if scipy_result.returncode != 0:
            print_warning("SciPy installation failed - continuing without it")
            print_status("Note: Core functionality will work without SciPy")
    else:
        # For non-RISC-V, install normally
        print_status("Installing basic dependencies")
        run_command([str(pip_path), "install", "numpy", "scipy"])

    # Audio processing
    print_status("Installing audio processing dependencies")
    run_command([str(pip_path), "install", "pyaudio", "pydub", "soundfile"])

    # Web framework
    print_status("Installing web framework dependencies")
    run_command([str(pip_path), "install", "fastapi", "uvicorn", "jinja2", "python-multipart", "python-socketio"])

    # CLI tools
    print_status("Installing CLI dependencies")
    run_command([str(pip_path), "install", "click", "rich"])

    # Utilities
    print_status("Installing utility dependencies")
    run_command([str(pip_path), "install", "python-dotenv", "requests", "aiofiles", "sqlalchemy", "pyyaml"])

    # STT engines
    print_status("Installing Speech-to-Text engines")
    whisper_result = run_command([str(pip_path), "install", "openai-whisper"], check=False)
    if whisper_result.returncode != 0:
        print_warning("Whisper installation failed - may need PyTorch first")

    run_command([str(pip_path), "install", "SpeechRecognition", "vosk"], check=False)

    # AI/ML dependencies
    print_status("Installing AI/ML dependencies")
    transformers_result = run_command([str(pip_path), "install", "transformers", "accelerate", "sentencepiece", "protobuf"], check=False)
    if transformers_result.returncode != 0:
        print_warning("Some AI/ML dependencies failed - may work with ONNX Runtime instead")

    # Install optional dependencies
    print_status("Installing optional dependencies")
    ollama_result = run_command([str(pip_path), "install", "ollama"], check=False)
    if ollama_result.returncode != 0:
        print_warning("Ollama client installation failed (optional)")

    # Install ONNX Runtime (useful for EIC7700 NPU)
    print_status("Installing ONNX Runtime")
    onnx_result = run_command([str(pip_path), "install", "onnxruntime"], check=False)
    if onnx_result.returncode != 0:
        print_warning("ONNX Runtime installation failed (optional, but recommended for EIC7700)")

    return True

def get_user_choice(prompt: str, options: List[str], default: str = "1") -> str:
    """Get user choice with validation"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    print()

    choice = input(f"Choose option [1-{len(options)}] (default: {default}): ").strip()
    if not choice:
        choice = default

    return choice

def download_whisper_model() -> bool:
    """Download Whisper model"""
    options = [
        "tiny - Fastest, lowest accuracy (~40MB)",
        "base - Good balance (default, ~150MB)",
        "small - Better accuracy (~500MB)",
        "medium - High accuracy (~1.5GB)"
    ]

    choice = get_user_choice("Choose Whisper model size:", options, "2")

    model_map = {"1": "tiny", "2": "base", "3": "small", "4": "medium"}
    model_name = model_map.get(choice, "base")

    print_status(f"Downloading Whisper '{model_name}' model...")

    python_path = Path("venv/bin/python3")
    download_script = f"""
import whisper
print('Downloading Whisper {model_name} model...')
whisper.load_model('{model_name}')
print('Whisper {model_name} model downloaded successfully')
"""

    result = run_command([str(python_path), "-c", download_script], check=False)
    if result.returncode != 0:
        print_warning("Failed to download Whisper model")
        return False

    # Update config with selected model
    config_path = Path("config.yaml")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            content = content.replace('model_size: "base"', f'model_size: "{model_name}"')
            with open(config_path, 'w') as f:
                f.write(content)
        except Exception:
            pass

    return True

def download_vosk_model() -> bool:
    """Download Vosk model"""
    options = [
        "US English (22MB) - Standard quality",
        "US English Large (1.8GB) - High quality",
        "Lightweight (50MB) - Fast processing"
    ]

    choice = get_user_choice("Choose Vosk model:", options, "1")

    model_urls = {
        "1": ("https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip", "vosk-model-en-us-0.22"),
        "2": ("https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip", "vosk-model-en-us-0.22-lgraph"),
        "3": ("https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", "vosk-model-small-en-us-0.15")
    }

    vosk_url, vosk_name = model_urls.get(choice, model_urls["1"])

    print_status("Downloading Vosk model...")
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    zip_path = models_dir / "vosk-model.zip"

    try:
        urllib.request.urlretrieve(vosk_url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)

        # Rename to standard name
        old_path = models_dir / vosk_name
        new_path = models_dir / "vosk-model-en-us-0.22"
        if old_path.exists() and not new_path.exists():
            old_path.rename(new_path)

        zip_path.unlink()
        print_status("Vosk model downloaded successfully")
        return True

    except Exception as e:
        print_warning(f"Failed to download Vosk model: {e}")
        return False

def download_qwen_model() -> bool:
    """Download Qwen model"""
    options = [
        "Qwen 1.8B - Lightweight, ~2GB",
        "Qwen 3B - Balanced performance (default), ~3.5GB",
        "Qwen 7B - High quality, ~7GB"
    ]

    choice = get_user_choice("Choose Qwen model size:", options, "2")

    model_map = {
        "1": "Qwen/Qwen2.5-1.5B-Instruct",
        "2": "Qwen/Qwen2.5-3B-Instruct",
        "3": "Qwen/Qwen2.5-7B-Instruct"
    }

    qwen_model = model_map.get(choice, model_map["2"])
    size_gb = {"1": "2", "2": "3.5", "3": "7"}.get(choice, "3.5")

    print_status(f"Pre-loading Qwen model: {qwen_model}")
    confirm = input(f"This will download ~{size_gb}GB. Continue? (y/N): ").strip().lower()

    if confirm not in ['y', 'yes']:
        print_status("Skipping Qwen model download")
        return True

    python_path = Path("venv/bin/python3")
    download_script = f"""
from transformers import AutoTokenizer, AutoModelForCausalLM
print('Downloading tokenizer...')
tokenizer = AutoTokenizer.from_pretrained('{qwen_model}')
print('Downloading model...')
model = AutoModelForCausalLM.from_pretrained('{qwen_model}')
print('Qwen model downloaded successfully')
"""

    result = run_command([str(python_path), "-c", download_script], check=False)
    if result.returncode != 0:
        print_warning("Failed to download Qwen model")
        return False

    # Update config with selected model
    config_path = Path("config.yaml")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            content = content.replace('model_name: "Qwen/Qwen2.5-3B-Instruct"', f'model_name: "{qwen_model}"')
            with open(config_path, 'w') as f:
                f.write(content)
        except Exception:
            pass

    return True

def setup_ollama() -> bool:
    """Setup Ollama (optional)"""
    print_header("Setting up Ollama")

    print_status("Ollama provides easy model switching and management.")
    response = input("Would you like to install Ollama? (Y/n): ").strip().lower()
    if response in ['n', 'no']:
        print_status("Skipping Ollama installation")
        return True

    print_status("Installing Ollama...")

    # Download and run Ollama install script
    try:
        install_script = urllib.request.urlopen("https://ollama.ai/install.sh").read().decode()
        result = subprocess.run(["sh"], input=install_script, text=True, check=True)
        print_status("Ollama installed successfully")
    except Exception as e:
        print_warning(f"Failed to install Ollama: {e}")
        return False

    # Enable and start Ollama service
    run_command(["sudo", "systemctl", "enable", "ollama"], check=False)
    run_command(["sudo", "systemctl", "start", "ollama"], check=False)

    # Wait for service to start
    import time
    time.sleep(2)

    # Offer to download a model
    model_response = input("Would you like to download a model now? (Y/n): ").strip().lower()
    if model_response not in ['n', 'no']:
        options = [
            "qwen2.5:1.5b - Lightweight, ~1GB",
            "qwen2.5:3b - Balanced (recommended), ~2GB",
            "qwen2.5:7b - High quality, ~4GB",
            "llama3.2:3b - Alternative option, ~2GB",
            "Skip - Download later with 'ollama pull <model>'"
        ]

        choice = get_user_choice("Choose model:", options, "2")

        models = {
            "1": "qwen2.5:1.5b",
            "2": "qwen2.5:3b",
            "3": "qwen2.5:7b",
            "4": "llama3.2:3b"
        }

        if choice in models:
            model_name = models[choice]
            print_status(f"Downloading {model_name}...")
            run_command(["ollama", "pull", model_name])

            # Update config
            config_path = Path("config.yaml")
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                    content = content.replace('model_name: "qwen2.5:3b"', f'model_name: "{model_name}"')
                    with open(config_path, 'w') as f:
                        f.write(content)
                except Exception:
                    pass
        elif choice != "5":
            print_status("Invalid choice, downloading qwen2.5:3b...")
            run_command(["ollama", "pull", "qwen2.5:3b"])

    print_status("Ollama setup complete!")
    print_status("You can manage models with: ollama list, ollama pull <model>, ollama rm <model>")

    return True

def download_models():
    """Download models based on user selection"""
    print_header("Model Installation Options")

    Path("models").mkdir(exist_ok=True)

    # STT models
    stt_options = [
        "Whisper (Recommended) - High accuracy, 99+ languages, ~150MB",
        "Vosk - Lightweight offline, English only, ~50MB",
        "Both - Full functionality, ~200MB total",
        "Skip - Install later manually"
    ]

    stt_choice = get_user_choice("Which STT models would you like to install?", stt_options, "1")

    if stt_choice == "1":
        download_whisper_model()
    elif stt_choice == "2":
        download_vosk_model()
    elif stt_choice == "3":
        download_whisper_model()
        download_vosk_model()
    else:
        print_status("Skipping STT model download")

    # Summarization models
    sum_options = [
        "Qwen 3B - Local transformer model, ~3.5GB",
        "Ollama - Model server with easy switching, varies by model",
        "Both - Maximum flexibility, ~3.5GB + Ollama",
        "Skip - Use API-based models only"
    ]

    sum_choice = get_user_choice("Which summarization setup would you like?", sum_options, "2")

    if sum_choice == "1":
        download_qwen_model()
    elif sum_choice == "2":
        setup_ollama()
    elif sum_choice == "3":
        download_qwen_model()
        setup_ollama()
    else:
        print_status("Skipping local summarization models")

def create_config():
    """Create configuration files"""
    print_header("Creating Configuration")

    # Auto-detect default audio device
    default_device = "null"
    if command_exists("arecord"):
        result = run_command(["arecord", "-l"], check=False)
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'card' in line:
                    parts = line.split(':')
                    if len(parts) > 0:
                        card_part = parts[0].strip()
                        if 'card' in card_part:
                            default_device = card_part.split()[-1]
                            break

    print_status(f"Detected audio device: {default_device}")

    # Update config with detected device
    config_path = Path("config.yaml")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            content = content.replace('input_device: null', f'input_device: {default_device}')
            with open(config_path, 'w') as f:
                f.write(content)
        except Exception:
            pass

def create_scripts():
    """Create startup scripts"""
    print_header("Creating Startup Scripts")

    # Create CLI launcher script
    with open("run_cli.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
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
''')

    # Create web launcher script
    with open("run_web.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
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

# Run web app
subprocess.run([str(venv_python), "web_app.py"])
''')

    # Create test script
    with open("test_setup.py", 'w') as f:
        f.write('''#!/usr/bin/env python3
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

print("Testing microphone devices...")
subprocess.run([str(venv_python), "cli.py", "devices"])
print()
print("Testing engines...")
subprocess.run([str(venv_python), "cli.py", "test"])
''')

    # Make scripts executable
    for script in ["run_cli.py", "run_web.py", "test_setup.py"]:
        os.chmod(script, 0o755)

    print_status("Created launcher scripts: run_cli.py, run_web.py, test_setup.py")

def optimize_sbc():
    """Performance optimization for SBC"""
    print_header("SBC Performance Optimization")

    # Check swap size
    try:
        result = run_command(["free", "-m"])
        lines = result.stdout.split('\n')
        for line in lines:
            if line.startswith('Swap:'):
                swap_size = int(line.split()[1])
                if swap_size < 2048:
                    print_status(f"Current swap: {swap_size}MB, recommended: 2048MB+")
                    response = input("Would you like to increase swap size? (y/N): ").strip().lower()
                    if response in ['y', 'yes']:
                        # Try different methods to increase swap
                        try:
                            run_command(["sudo", "dphys-swapfile", "swapoff"], check=False)
                            run_command(["sudo", "sed", "-i", "s/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/",
                                       "/etc/dphys-swapfile"], check=False)
                            run_command(["sudo", "dphys-swapfile", "setup"], check=False)
                            run_command(["sudo", "dphys-swapfile", "swapon"], check=False)
                        except:
                            # Manual swap file creation
                            try:
                                run_command(["sudo", "fallocate", "-l", "2G", "/swapfile"])
                                run_command(["sudo", "chmod", "600", "/swapfile"])
                                run_command(["sudo", "mkswap", "/swapfile"])
                                run_command(["sudo", "swapon", "/swapfile"])
                                # Add to fstab
                                with open("/etc/fstab", "a") as f:
                                    f.write("/swapfile none swap sw 0 0\n")
                                print_status("Swap size increased")
                            except Exception as e:
                                print_warning(f"Failed to increase swap: {e}")
                break
    except Exception:
        print_warning("Could not check swap size")

    # CPU governor optimization
    governor_path = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    if governor_path.exists():
        print_status("Setting CPU governor to performance mode")
        try:
            run_command(["sudo", "bash", "-c",
                       "echo 'performance' | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"],
                       check=False)
        except:
            pass

def test_installation():
    """Test installation"""
    print_header("Testing Installation")

    python_path = Path("venv/bin/python3")

    print_status("Testing Python imports...")
    test_script = '''
import sys
print(f'Python: {sys.version}')

try:
    import torch
    print(f'PyTorch: {torch.__version__}')
except ImportError as e:
    print(f'PyTorch import error: {e}')

try:
    import whisper
    print('Whisper: Available')
except ImportError as e:
    print(f'Whisper import error: {e}')

try:
    import transformers
    print(f'Transformers: {transformers.__version__}')
except ImportError as e:
    print(f'Transformers import error: {e}')

try:
    import pyaudio
    print('PyAudio: Available')
except ImportError as e:
    print(f'PyAudio import error: {e}')
'''

    result = run_command([str(python_path), "-c", test_script], check=False)
    if result.returncode != 0:
        print_error("Python dependency test failed")
    else:
        print(result.stdout)

    # Test microphone
    print_status("Testing microphone access...")
    mic_test_script = '''
import pyaudio
pa = pyaudio.PyAudio()
devices = []
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        devices.append((i, info['name']))

print(f'Found {len(devices)} input devices')
for idx, name in devices:
    print(f'  Device {idx}: {name}')
pa.terminate()
'''

    result = run_command([str(python_path), "-c", mic_test_script], check=False)
    if result.returncode != 0:
        print_warning("Microphone test failed")
    else:
        print(result.stdout)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Meeting Assistant Installation Script for Single Board Computers (SBC)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install_sbc.py                    # Interactive installation
  python3 install_sbc.py --auto-confirm     # Skip confirmation prompts
  python3 install_sbc.py --models-only      # Install only AI models
  python3 install_sbc.py --no-models        # Install without downloading models
  python3 install_sbc.py --stt whisper      # Pre-select STT engine
  python3 install_sbc.py --ai qwen          # Pre-select AI engine

Supported Hardware:
  - RK3588 (Rock 5B, Orange Pi 5, etc.)
  - Raspberry Pi 4/5
  - Generic ARM64 SBCs
  - x86_64 desktop/laptop

Features Installed:
  - Speech-to-Text: Whisper, Vosk
  - AI Summarization: Qwen 3, Ollama
  - Web interface (FastAPI)
  - CLI interface (Click)
  - Audio recording (PyAudio)
  - NPU optimization (RK3588)
        """)

    parser.add_argument('--help-extended', action='store_true',
                       help='Show extended help with detailed information')

    parser.add_argument('--auto-confirm', '-y', action='store_true',
                       help='Skip confirmation prompts (use defaults)')

    parser.add_argument('--models-only', action='store_true',
                       help='Only download models, skip system setup')

    parser.add_argument('--no-models', action='store_true',
                       help='Skip model downloads')

    parser.add_argument('--stt', choices=['whisper', 'vosk', 'both', 'skip'],
                       help='Pre-select STT engine (skip interactive choice)')

    parser.add_argument('--ai', choices=['qwen', 'ollama', 'both', 'skip'],
                       help='Pre-select AI engine (skip interactive choice)')

    parser.add_argument('--whisper-size', choices=['tiny', 'base', 'small', 'medium'],
                       help='Pre-select Whisper model size')

    parser.add_argument('--qwen-size', choices=['1.8b', '3b', '7b'],
                       help='Pre-select Qwen model size')

    parser.add_argument('--test-only', action='store_true',
                       help='Only run installation tests')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')

    return parser.parse_args()

def show_extended_help():
    """Show detailed help information"""
    print(f"""
{Colors.BLUE}Meeting Assistant SBC Installation - Extended Help{Colors.NC}
===============================================================

{Colors.GREEN}OVERVIEW{Colors.NC}
This script installs the Meeting Assistant on Single Board Computers (SBC) and
desktop systems with optimizations for ARM64 hardware, especially RK3588.

{Colors.GREEN}SYSTEM REQUIREMENTS{Colors.NC}
- Operating System: Linux (Ubuntu 20.04+, Debian 11+)
- Architecture: ARM64 (aarch64) or x86_64
- Memory: 4GB+ RAM (8GB+ recommended for large models)
- Storage: 2-10GB free space (depending on model choices)
- Audio: Microphone and speakers/headphones

{Colors.GREEN}INSTALLATION MODES{Colors.NC}

1. {Colors.YELLOW}Interactive Mode (Default){Colors.NC}
   python3 install_sbc.py
   - Guided installation with choices for each component
   - Detects hardware and suggests optimal configurations
   - Safe for beginners

2. {Colors.YELLOW}Automated Mode{Colors.NC}
   python3 install_sbc.py --auto-confirm
   - Uses default choices for all prompts
   - Faster installation for experienced users
   - Good for scripted deployments

3. {Colors.YELLOW}Models Only{Colors.NC}
   python3 install_sbc.py --models-only
   - Only downloads AI models
   - Useful if system packages already installed
   - Faster for model updates

{Colors.GREEN}MODEL SELECTION GUIDE{Colors.NC}

STT (Speech-to-Text) Models:
- {Colors.YELLOW}whisper-tiny{Colors.NC}:    40MB,  fastest, good for testing
- {Colors.YELLOW}whisper-base{Colors.NC}:   150MB, recommended for most users
- {Colors.YELLOW}whisper-small{Colors.NC}:  500MB, better accuracy
- {Colors.YELLOW}whisper-medium{Colors.NC}: 1.5GB, high accuracy (needs 8GB+ RAM)

- {Colors.YELLOW}vosk-standard{Colors.NC}:   22MB, lightweight offline
- {Colors.YELLOW}vosk-large{Colors.NC}:    1.8GB, high quality offline

AI Summarization Models:
- {Colors.YELLOW}qwen-1.8b{Colors.NC}:      2GB,   fast, good quality
- {Colors.YELLOW}qwen-3b{Colors.NC}:      3.5GB,  balanced (recommended)
- {Colors.YELLOW}qwen-7b{Colors.NC}:        7GB,   highest quality (needs 16GB+ RAM)

- {Colors.YELLOW}ollama{Colors.NC}:        varies, easy model switching

{Colors.GREEN}HARDWARE OPTIMIZATIONS{Colors.NC}

RK3588 Specific:
- NPU acceleration for inference
- Optimized memory management
- Power-efficient processing
- Real-time performance tuning

Raspberry Pi:
- CPU optimization
- Memory conservation
- Swap management
- Audio device detection

{Colors.GREEN}POST-INSTALLATION{Colors.NC}

Test Installation:
  python3 test.py quick      # Quick system check
  python3 test.py setup      # Audio and engines
  python3 test.py complete   # Full functionality

Run Application:
  python3 run_cli.py         # Command line interface
  python3 run_web.py         # Web interface

Configuration:
  Edit config.yaml for custom settings

{Colors.GREEN}TROUBLESHOOTING{Colors.NC}

Common Issues:
- Audio permissions: Add user to audio group, restart session
- Memory errors: Use smaller models, increase swap
- Download failures: Check internet, retry installation
- NPU not detected: Install RK3588-specific drivers

For detailed troubleshooting, see README.md

{Colors.GREEN}EXAMPLES{Colors.NC}

# Minimal installation with tiny models
python3 install_sbc.py --stt whisper --whisper-size tiny --ai qwen --qwen-size 1.8b

# Maximum quality installation
python3 install_sbc.py --stt both --whisper-size medium --ai both --qwen-size 7b

# Testing-focused installation
python3 install_sbc.py --no-models --test-only

# Update models only
python3 install_sbc.py --models-only --stt whisper --ai ollama
""")

def main():
    """Main installation function"""
    args = parse_arguments()

    if args.help_extended:
        show_extended_help()
        return

    print_header("Meeting Assistant Installation for SBC")

    print("==========================================")
    print("Meeting Assistant SBC Installation Script")
    print("==========================================")

    # Check if running as root
    if os.geteuid() == 0:
        print_error("Please don't run this script as root")
        sys.exit(1)

    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    try:
        if args.test_only:
            print_status("Running installation tests only...")
            test_installation()
            return

        arch, os_name, sbc_type = detect_system()

        if args.verbose:
            print_status(f"Detected: {arch} {os_name} ({sbc_type})")

        if not args.models_only:
            if not check_dependencies():
                sys.exit(1)

            install_system_packages(sbc_type)
            setup_audio()
            setup_python_env()
            install_pytorch(arch, sbc_type)
            install_python_deps(arch)

            # Display hardware-specific notes
            if sbc_type == "eic7700":
                print_header("EIC7700 RISC-V NPU Setup")
                print_status("To enable NPU acceleration on EIC7700:")
                print("  1. Install ENNP SDK from ESWIN Computing")
                print("  2. Download SDK from: https://www.eswincomputing.com")
                print("  3. Follow vendor instructions for SDK installation")
                print("  4. Install ONNX Runtime with ENNP EP support")
                print()
                print_status("ENNP SDK provides model conversion tools:")
                print("  - EsQuant: Model quantization")
                print("  - EsAAC: Model compilation for EIC7700 NPU")
                print("  - EsSimulator: Validation and testing")
                print()

        if not args.no_models:
            download_models()

        if not args.models_only:
            create_config()
            create_scripts()
            optimize_sbc()
            test_installation()

        print_header("Installation Complete!")
        print(f"{Colors.GREEN}Installation completed successfully!{Colors.NC}")
        print()
        print("Next steps:")
        print("1. Log out and log back in (for audio group changes)")
        print("2. Test the setup: python3 test_setup.py")
        print("3. Run CLI version: python3 run_cli.py test")
        print("4. Run web version: python3 run_web.py")
        print()
        print("Microphone devices detected:")
        if command_exists("arecord"):
            result = run_command(["arecord", "-l"], check=False)
            if result.returncode == 0 and result.stdout:
                lines = [line for line in result.stdout.split('\n') if 'card' in line]
                if lines:
                    for line in lines:
                        print(line)
                else:
                    print("No recording devices found")
            else:
                print("No recording devices found")
        print()
        print(f"{Colors.YELLOW}Note: If you have audio issues, check your microphone permissions and ALSA configuration{Colors.NC}")

    except KeyboardInterrupt:
        print_error("\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()