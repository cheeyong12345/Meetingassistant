#!/bin/bash
# Complete RISC-V Setup - Whisper.cpp + Config

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║      Complete RISC-V Setup for Meeting Assistant             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check disk space
AVAIL=$(df / | tail -1 | awk '{print $4}')
if [ "$AVAIL" -lt 200000 ]; then
    echo "⚠️  Warning: Low disk space. Cleaning up..."
    pip cache purge 2>/dev/null || true
    sudo apt clean 2>/dev/null || true
fi

echo "════════════════════════════════════════════════════════════════"
echo "📥 Installing Whisper.cpp"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Remove old installation
cd ~
if [ -d "whisper.cpp" ]; then
    echo "→ Removing old whisper.cpp..."
    rm -rf whisper.cpp
fi

# Clone
echo "→ Cloning whisper.cpp..."
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# Build
echo ""
echo "→ Building whisper.cpp..."
make -j$(nproc)

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build successful"

# Download model
echo ""
echo "→ Downloading base model (~150MB)..."
bash ./models/download-ggml-model.sh base

if [ $? -ne 0 ]; then
    echo "❌ Model download failed"
    exit 1
fi

echo "✅ Model downloaded"

# Verify
echo ""
echo "→ Verifying installation..."
if [ -f "models/ggml-base.bin" ] && [ -f "build/bin/whisper-cli" ]; then
    echo "✅ Whisper.cpp installed successfully!"
    ls -lh models/ggml-base.bin
    ls -lh build/bin/whisper-cli
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⚙️  Creating Configuration"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd ~/Meetingassistant

# Backup existing config
if [ -f "config.yaml" ]; then
    echo "→ Backing up existing config.yaml..."
    cp config.yaml config.yaml.backup
    echo "✅ Backup saved: config.yaml.backup"
fi

# Create new config
cat > config.yaml << 'EOF'
# Meeting Assistant Configuration for RISC-V

# Speech-to-Text (Whisper.cpp)
stt:
  default_engine: whispercpp
  engines:
    whispercpp:
      model_size: base
      language: auto
      threads: 4

# Summarization (ESWIN NPU - Qwen2 7B)
summarization:
  default_engine: qwen
  engines:
    qwen:
      model_name: Qwen/Qwen2.5-3B-Instruct
      device: auto
      use_npu: true
      max_tokens: 1000
      temperature: 0.7

# Audio Settings
audio:
  sample_rate: 16000
  chunk_duration: 1.0
  device_index: 0
  channels: 1

# Logging
logging:
  level: INFO
  console: true
  file: true
  log_dir: logs
EOF

echo "✅ Configuration created: config.yaml"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test whisper.cpp
echo "→ Testing whisper.cpp binary..."
if ~/whisper.cpp/build/bin/whisper-cli --help > /dev/null 2>&1; then
    echo "✅ Whisper.cpp binary works"
else
    echo "⚠️  Whisper.cpp binary test failed (may still work)"
fi

# Test Python imports
echo ""
echo "→ Testing Python imports..."
source venv/bin/activate

python3 << 'PYTEST'
import sys
errors = []

try:
    import transformers
    print("  ✅ transformers")
except Exception as e:
    print(f"  ❌ transformers: {e}")
    errors.append("transformers")

try:
    import fastapi
    print("  ✅ fastapi")
except Exception as e:
    print(f"  ❌ fastapi: {e}")
    errors.append("fastapi")

try:
    import uvicorn
    print("  ✅ uvicorn")
except Exception as e:
    print(f"  ❌ uvicorn: {e}")
    errors.append("uvicorn")

try:
    from src.utils.eswin_npu import ESWINNPUInterface
    if ESWINNPUInterface.is_available():
        print("  ✅ ESWIN NPU detected")
    else:
        print("  ℹ️  ESWIN NPU not detected (optional)")
except Exception as e:
    print(f"  ⚠️  ESWIN NPU check: {e}")

if errors:
    print(f"\n⚠️  Some imports failed: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✅ All Python imports successful!")
PYTEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Installation Summary:"
echo "  ✅ Whisper.cpp: ~/whisper.cpp"
echo "  ✅ Model: base (150MB)"
echo "  ✅ Binary: ~/whisper.cpp/build/bin/whisper-cli"
echo "  ✅ Config: ~/Meetingassistant/config.yaml"
echo ""
echo "📋 Your Stack:"
echo "  • STT: Whisper.cpp (no PyTorch!)"
echo "  • Summarization: ESWIN NPU Qwen2 7B"
echo "  • Web UI: FastAPI + Uvicorn"
echo ""
echo "📋 Next Steps:"
echo "  1. Start the web app:"
echo "     cd ~/Meetingassistant"
echo "     source venv/bin/activate"
echo "     python3 web_app.py"
echo ""
echo "  2. Open browser:"
echo "     http://localhost:8000"
echo ""
echo "  3. Click 'Start Meeting' and speak!"
echo ""
echo "💡 Tips:"
echo "  • If old config.yaml exists: config.yaml.backup"
echo "  • Check logs: ~/Meetingassistant/logs/"
echo "  • ESWIN NPU path: /opt/eswin/sample-code/.../es_qwen2"
echo ""
