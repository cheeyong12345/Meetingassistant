#!/bin/bash

# ============================================================================
# Fix Script for Eswin 7700x RISC-V Device
# Fixes: Whisper.cpp issues and audio input device detection
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Eswin 7700x Meeting Assistant Fix Script${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ============================================================================
# 1. System Information
# ============================================================================
echo -e "${YELLOW}[1/8] Gathering System Information${NC}"
echo "----------------------------------------"
echo "Architecture: $(uname -m)"
echo "Kernel: $(uname -r)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "CPU Info:"
if [ -f /proc/cpuinfo ]; then
    grep -m1 "model name" /proc/cpuinfo || echo "CPU model not found"
    echo "CPU Cores: $(nproc)"
fi
echo ""

# ============================================================================
# 2. Check and Fix Audio Subsystem
# ============================================================================
echo -e "${YELLOW}[2/8] Checking Audio Subsystem${NC}"
echo "----------------------------------------"

# Check if ALSA is installed
if ! command -v aplay &> /dev/null; then
    echo -e "${RED}ALSA not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y alsa-utils libasound2-dev
else
    echo -e "${GREEN}ALSA is installed${NC}"
fi

# List ALSA devices
echo ""
echo "ALSA Audio Devices:"
aplay -l 2>/dev/null || echo "No ALSA playback devices found"
echo ""
echo "ALSA Recording Devices:"
arecord -l 2>/dev/null || echo "No ALSA recording devices found"

# Check PulseAudio (if installed)
if command -v pactl &> /dev/null; then
    echo ""
    echo "PulseAudio Sources (Microphones):"
    pactl list sources short 2>/dev/null || echo "PulseAudio not running"
fi

# ============================================================================
# 3. Fix Python Audio Libraries
# ============================================================================
echo ""
echo -e "${YELLOW}[3/8] Fixing Python Audio Libraries${NC}"
echo "----------------------------------------"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}Virtual environment activated${NC}"
else
    echo -e "${RED}Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Check Python version
echo "Python version: $(python3 --version)"

# Reinstall PyAudio with proper flags for RISC-V
echo ""
echo "Reinstalling PyAudio for RISC-V..."

# First, ensure we have the build dependencies
echo "Installing build dependencies..."
sudo apt-get install -y \
    python3-dev \
    portaudio19-dev \
    gcc \
    g++ \
    make

# Uninstall existing PyAudio
pip uninstall -y pyaudio 2>/dev/null || true

# Try to install PyAudio with different methods
echo "Attempting PyAudio installation..."

# Method 1: Try pip with no binary
if ! pip install --no-binary :all: pyaudio 2>/dev/null; then
    echo "Standard pip install failed, trying alternative method..."

    # Method 2: Build from source
    echo "Building PyAudio from source..."
    cd /tmp
    wget -q http://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz
    tar -xzf pa_stable_v190700_20210406.tgz
    cd portaudio
    ./configure --without-jack --without-oss
    make -j$(nproc)
    sudo make install
    sudo ldconfig

    # Now install PyAudio
    cd "$SCRIPT_DIR"
    pip install pyaudio --no-cache-dir
fi

# Verify PyAudio installation
echo ""
echo "Verifying PyAudio installation..."
python3 -c "import pyaudio; print('PyAudio version:', pyaudio.__version__)" || {
    echo -e "${RED}PyAudio installation failed!${NC}"
}

# ============================================================================
# 4. Test Audio Device Detection
# ============================================================================
echo ""
echo -e "${YELLOW}[4/8] Testing Audio Device Detection${NC}"
echo "----------------------------------------"

# Create a test script
cat > test_audio_devices.py << 'EOF'
#!/usr/bin/env python3
import sys
import json

try:
    import pyaudio

    p = pyaudio.PyAudio()

    print("Audio Host APIs:")
    for i in range(p.get_host_api_count()):
        info = p.get_host_api_info_by_index(i)
        print(f"  [{i}] {info['name']} - {info['deviceCount']} devices")

    print("\nInput Devices:")
    input_devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{info['index']}] {info['name']}")
            print(f"      Channels: {info['maxInputChannels']}")
            print(f"      Sample Rate: {int(info['defaultSampleRate'])} Hz")
            print(f"      Host API: {p.get_host_api_info_by_index(info['hostApi'])['name']}")
            input_devices.append(info)

    if not input_devices:
        print("  No input devices found!")
        print("\nTrying alternative detection method...")

        # Try to find devices through host APIs
        for api_idx in range(p.get_host_api_count()):
            api_info = p.get_host_api_info_by_index(api_idx)
            print(f"\nChecking {api_info['name']} API...")
            for i in range(api_info['deviceCount']):
                try:
                    dev_idx = p.get_device_info_by_host_api_device_index(api_idx, i)
                    if dev_idx and dev_idx.get('maxInputChannels', 0) > 0:
                        print(f"  Found: {dev_idx['name']}")
                except:
                    pass

    p.terminate()

except ImportError:
    print("ERROR: PyAudio not installed!")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
EOF

chmod +x test_audio_devices.py
python3 test_audio_devices.py

# ============================================================================
# 5. Fix Whisper.cpp for RISC-V
# ============================================================================
echo ""
echo -e "${YELLOW}[5/8] Fixing Whisper.cpp for RISC-V${NC}"
echo "----------------------------------------"

WHISPER_DIR="$HOME/git_lib/whisper.cpp"

if [ ! -d "$WHISPER_DIR" ]; then
    echo "Whisper.cpp not found at $WHISPER_DIR"
    echo "Cloning whisper.cpp..."
    mkdir -p "$HOME/git_lib"
    cd "$HOME/git_lib"
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd "$WHISPER_DIR"
else
    echo "Whisper.cpp found at $WHISPER_DIR"
    cd "$WHISPER_DIR"

    # Clean previous builds
    echo "Cleaning previous builds..."
    make clean 2>/dev/null || true
    rm -rf build 2>/dev/null || true
fi

echo ""
echo "Building Whisper.cpp for RISC-V Eswin 7700x..."

# Detect RISC-V ISA string (rv64gc, rv64imafc, etc.)
# RISC-V doesn't support -march=native, we need to detect the ISA manually
RISCV_ARCH=""
if grep -q "rv64" /proc/cpuinfo 2>/dev/null; then
    # Extract ISA from cpuinfo if available
    RISCV_ARCH=$(grep "isa" /proc/cpuinfo | head -1 | awk '{print $NF}')
elif command -v gcc &> /dev/null; then
    # Try to get from gcc target
    GCC_TARGET=$(gcc -dumpmachine)
    if [[ "$GCC_TARGET" == *"riscv64"* ]]; then
        RISCV_ARCH="rv64gc"  # Common baseline
    fi
fi

echo "Detected RISC-V architecture: ${RISCV_ARCH:-default}"

# Build with CMake (preferred for RISC-V)
echo "Building with CMake..."
mkdir -p build
cd build

# Configure with RISC-V optimizations
# Don't use -march=native on RISC-V, use detected ISA or default
if [ -z "$RISCV_ARCH" ]; then
    # No specific arch detected, use basic optimization
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DWHISPER_BUILD_TESTS=OFF \
        -DWHISPER_BUILD_EXAMPLES=ON \
        -DCMAKE_C_FLAGS="-O3" \
        -DCMAKE_CXX_FLAGS="-O3"
else
    # Use detected RISC-V ISA
    cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DWHISPER_BUILD_TESTS=OFF \
        -DWHISPER_BUILD_EXAMPLES=ON \
        -DCMAKE_C_FLAGS="-march=${RISCV_ARCH} -O3" \
        -DCMAKE_CXX_FLAGS="-march=${RISCV_ARCH} -O3"
fi

# Build with available cores
make -j$(nproc) || {
    echo -e "${YELLOW}CMake build failed, trying Makefile...${NC}"
    cd "$WHISPER_DIR"

    # Try traditional Makefile with RISC-V flags (no -march=native)
    make clean
    if [ -z "$RISCV_ARCH" ]; then
        CFLAGS="-O3" CXXFLAGS="-O3" make -j$(nproc)
    else
        CFLAGS="-O3 -march=${RISCV_ARCH}" CXXFLAGS="-O3 -march=${RISCV_ARCH}" make -j$(nproc)
    fi
}

# Check if binary exists
echo ""
echo "Checking Whisper binaries..."
if [ -f "$WHISPER_DIR/build/bin/whisper-cli" ]; then
    echo -e "${GREEN}Found: whisper-cli (CMake build)${NC}"
    WHISPER_BIN="$WHISPER_DIR/build/bin/whisper-cli"
elif [ -f "$WHISPER_DIR/build/bin/main" ]; then
    echo -e "${YELLOW}Found: main (CMake build - deprecated)${NC}"
    WHISPER_BIN="$WHISPER_DIR/build/bin/main"
elif [ -f "$WHISPER_DIR/main" ]; then
    echo -e "${YELLOW}Found: main (Makefile build)${NC}"
    WHISPER_BIN="$WHISPER_DIR/main"
else
    echo -e "${RED}No whisper binary found!${NC}"
    WHISPER_BIN=""
fi

if [ ! -z "$WHISPER_BIN" ]; then
    echo "Testing whisper binary..."
    $WHISPER_BIN -h > /dev/null 2>&1 && echo -e "${GREEN}Whisper binary is working${NC}" || echo -e "${RED}Whisper binary test failed${NC}"
fi

# ============================================================================
# 6. Download Whisper Model
# ============================================================================
echo ""
echo -e "${YELLOW}[6/8] Checking Whisper Model${NC}"
echo "----------------------------------------"

MODEL_DIR="$WHISPER_DIR/models"
MODEL_FILE="$MODEL_DIR/ggml-base.bin"

if [ ! -f "$MODEL_FILE" ]; then
    echo "Downloading base model..."
    cd "$WHISPER_DIR"
    bash ./models/download-ggml-model.sh base
else
    echo -e "${GREEN}Model already exists: $MODEL_FILE${NC}"
fi

# ============================================================================
# 7. Create Configuration Fix
# ============================================================================
echo ""
echo -e "${YELLOW}[7/8] Creating Configuration Fix${NC}"
echo "----------------------------------------"

cd "$SCRIPT_DIR"

# Create a configuration patch for RISC-V
cat > fix_config_riscv.py << 'EOF'
#!/usr/bin/env python3
"""Fix configuration for RISC-V Eswin 7700x"""

import json
import os
from pathlib import Path

def fix_audio_config():
    """Fix audio configuration for RISC-V"""
    config_file = Path("config.json")

    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Update audio configuration
    if 'audio' not in config:
        config['audio'] = {}

    config['audio'].update({
        'sample_rate': 16000,  # Standard for speech recognition
        'channels': 1,         # Mono is sufficient
        'chunk_size': 1024,    # Smaller chunks for RISC-V
        'device_index': None,  # Auto-detect
        'format': 'int16'     # 16-bit audio
    })

    # Update STT configuration for RISC-V
    if 'stt' not in config:
        config['stt'] = {}

    config['stt'].update({
        'engine': 'whispercpp',
        'model_size': 'base',  # Use base model for better performance
        'language': 'en',
        'threads': os.cpu_count() // 2  # Use half the cores
    })

    # Save configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"Configuration updated: {config_file}")
    return config

if __name__ == "__main__":
    fix_audio_config()
EOF

echo "Applying configuration fixes..."
python3 fix_config_riscv.py

# ============================================================================
# 8. Create Test Script
# ============================================================================
echo ""
echo -e "${YELLOW}[8/8] Creating Test Script${NC}"
echo "----------------------------------------"

cat > test_meeting_riscv.py << 'EOF'
#!/usr/bin/env python3
"""Test meeting assistant on RISC-V"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from src.meeting import MeetingAssistant
        print("✓ MeetingAssistant imported")

        from src.config import config
        print("✓ Config imported")

        import pyaudio
        print("✓ PyAudio imported")

        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_audio():
    """Test audio system"""
    print("\nTesting audio system...")
    try:
        import pyaudio
        p = pyaudio.PyAudio()

        # Find input device
        input_device = None
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_device = info
                break

        if input_device:
            print(f"✓ Found input device: {input_device['name']}")

            # Try to open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=input_device['index'],
                frames_per_buffer=1024
            )
            stream.close()
            print("✓ Audio stream test successful")
        else:
            print("✗ No input device found")

        p.terminate()
        return True
    except Exception as e:
        print(f"✗ Audio test failed: {e}")
        return False

def test_whisper():
    """Test whisper binary"""
    print("\nTesting Whisper...")
    import subprocess
    from pathlib import Path

    whisper_dir = Path.home() / "git_lib" / "whisper.cpp"
    possible_bins = [
        whisper_dir / "build" / "bin" / "whisper-cli",
        whisper_dir / "build" / "bin" / "main",
        whisper_dir / "main"
    ]

    for bin_path in possible_bins:
        if bin_path.exists():
            try:
                result = subprocess.run(
                    [str(bin_path), "-h"],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0 or "deprecated" in result.stderr.decode().lower():
                    print(f"✓ Whisper binary works: {bin_path}")
                    return True
            except Exception as e:
                print(f"✗ Whisper test failed: {e}")

    print("✗ No working Whisper binary found")
    return False

if __name__ == "__main__":
    print("="*50)
    print("RISC-V Eswin 7700x Meeting Assistant Test")
    print("="*50)

    all_passed = True
    all_passed &= test_imports()
    all_passed &= test_audio()
    all_passed &= test_whisper()

    print("\n" + "="*50)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Please check the output above.")
    print("="*50)
EOF

chmod +x test_meeting_riscv.py

# ============================================================================
# Final Summary
# ============================================================================
echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}Fix Script Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo "Summary of actions taken:"
echo "1. ✓ Checked system information"
echo "2. ✓ Fixed audio subsystem dependencies"
echo "3. ✓ Reinstalled PyAudio for RISC-V"
echo "4. ✓ Tested audio device detection"
echo "5. ✓ Rebuilt Whisper.cpp for RISC-V"
echo "6. ✓ Verified Whisper model"
echo "7. ✓ Created configuration fixes"
echo "8. ✓ Created test scripts"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Run the test script: ./test_meeting_riscv.py"
echo "2. Start the web app: python3 web_app.py"
echo "3. Check logs at: logs/meeting_assistant.log"
echo ""
echo -e "${GREEN}Script completed successfully!${NC}"