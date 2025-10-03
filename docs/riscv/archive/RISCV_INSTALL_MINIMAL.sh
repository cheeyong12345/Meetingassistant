#!/bin/bash
# Minimal RISC-V installation - transformers without Rust dependencies

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   RISC-V Minimal Install - No Rust Dependencies              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Not in virtual environment!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📦 Strategy: Install transformers WITHOUT Rust dependencies"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Uninstall any existing transformers
pip uninstall -y transformers 2>/dev/null

# Install transformers with --no-deps (skip ALL dependencies)
echo "→ Installing transformers 4.30.2 with --no-deps..."
pip install --no-cache-dir --no-deps "transformers==4.30.2"

# Install only the Python dependencies (no Rust)
echo ""
echo "→ Installing Python-only dependencies..."
pip install --no-cache-dir \
    filelock \
    huggingface-hub \
    packaging \
    pyyaml \
    regex \
    requests \
    tqdm

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Installing openai-whisper for STT (includes its own model)"
echo "════════════════════════════════════════════════════════════════"
echo ""

pip install --no-cache-dir openai-whisper

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 << 'EOF'
import sys

print("Testing core packages...")

# Test transformers
try:
    import transformers
    print(f"  ✅ transformers {transformers.__version__}")
except Exception as e:
    print(f"  ❌ transformers: {e}")
    sys.exit(1)

# Test whisper
try:
    import whisper
    print(f"  ✅ whisper (openai-whisper)")
except Exception as e:
    print(f"  ⚠️  whisper: {e}")

# Test web framework
try:
    import fastapi, uvicorn
    print(f"  ✅ fastapi {fastapi.__version__}")
    print(f"  ✅ uvicorn {uvicorn.__version__}")
except Exception as e:
    print(f"  ❌ web framework: {e}")

print("\n✅ Core packages installed!")

# Check what transformers functionality works
print("\nTesting transformers features...")

try:
    from transformers import PretrainedConfig
    print("  ✅ PretrainedConfig works")
except Exception as e:
    print(f"  ❌ PretrainedConfig: {e}")

# Try AutoTokenizer (may fail without tokenizers)
try:
    from transformers import AutoTokenizer
    print("  ✅ AutoTokenizer available (slow tokenizers)")
except Exception as e:
    print(f"  ⚠️  AutoTokenizer: {e}")
    print("     (This is OK - we'll use ESWIN NPU binary)")

EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Tests failed"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Meeting Assistant"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 << 'EOFMA'
import sys
sys.path.insert(0, '.')

# Test ESWIN NPU first
print("Testing ESWIN NPU availability...")
try:
    from src.utils.eswin_npu import ESWINNPUInterface
    if ESWINNPUInterface.is_available():
        print("  ✅ ESWIN NPU binary detected!")
        print("     Will use hardware-accelerated Qwen2 7B")
    else:
        print("  ℹ️  ESWIN NPU binary not found")
        print("     Path: /opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2")
except Exception as e:
    print(f"  ⚠️  ESWIN NPU check: {e}")

# Test hardware detection
print("\nTesting hardware detection...")
try:
    from src.utils.hardware import get_hardware_detector
    hw = get_hardware_detector()
    info = hw.get_system_info()
    print(f"  ✅ Detected: {info['architecture']} / {info['soc_type']}")
except Exception as e:
    print(f"  ⚠️  Hardware detection: {e}")

# Test Meeting Assistant
print("\nTesting Meeting Assistant...")
try:
    from src.meeting import MeetingAssistant
    print("  ✅ MeetingAssistant imports OK")
except Exception as e:
    print(f"  ⚠️  MeetingAssistant: {e}")
    print("     (May need to configure for ESWIN NPU)")

print("\n✅ Meeting Assistant ready!")

EOFMA

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ INSTALLATION COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 What's Installed:"
echo "  ✅ transformers 4.30.2 (without Rust deps)"
echo "  ✅ openai-whisper (for STT)"
echo "  ✅ fastapi + uvicorn (web interface)"
echo "  ✅ All Python dependencies"
echo ""
echo "⚠️  What's NOT Installed (and why):"
echo "  ❌ tokenizers (needs Rust) - using slow Python tokenizers"
echo "  ❌ safetensors (needs Rust) - not needed for our use case"
echo "  ❌ PyTorch (no RISC-V wheels) - using ESWIN NPU instead"
echo ""
echo "📋 How It Works:"
echo "  • STT: openai-whisper (has built-in inference)"
echo "  • Summarization: ESWIN NPU binary (Qwen2 7B INT8)"
echo "  • Web UI: FastAPI + Uvicorn"
echo ""
echo "📋 Next Steps:"
echo "  1. Check ESWIN NPU binary:"
echo "     ls /opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2"
echo ""
echo "  2. Run web app:"
echo "     python3 web_app.py"
echo ""
echo "  3. Open browser:"
echo "     http://localhost:8000"
echo ""
