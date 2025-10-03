#!/bin/bash
# Fix config.yaml and install web dependencies for RISC-V

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║      Fix Config & Install Web Dependencies (RISC-V)          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📝 Fixing config.yaml"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found!"
    exit 1
fi

# Add server section if missing
if ! grep -q "^server:" config.yaml; then
    echo "→ Adding missing server section to config.yaml..."
    cat >> config.yaml << 'EOF'

# Server configuration
server:
  host: "0.0.0.0"
  port: 8000
  reload: true
EOF
    echo "✅ Server section added"
else
    echo "✅ Server section already exists"
fi

# Add storage section if missing
if ! grep -q "^storage:" config.yaml; then
    echo "→ Adding missing storage section to config.yaml..."
    cat >> config.yaml << 'EOF'

# Storage Configuration
storage:
  data_dir: "./data"
  meetings_dir: "./data/meetings"
  models_dir: "./models"
  database_url: "sqlite:///./data/meetings.db"
EOF
    echo "✅ Storage section added"
else
    echo "✅ Storage section already exists"
fi

# Add processing section if missing
if ! grep -q "^processing:" config.yaml; then
    echo "→ Adding missing processing section to config.yaml..."
    cat >> config.yaml << 'EOF'

# Processing settings
processing:
  real_time_stt: true
  auto_summarize: true
  speaker_detection: false
  chunk_duration: 30
  max_meeting_duration: 14400
EOF
    echo "✅ Processing section added"
else
    echo "✅ Processing section already exists"
fi

# Create directories
echo ""
echo "→ Creating required directories..."
mkdir -p data/meetings data/recordings data/transcripts data/summaries models logs
echo "✅ Directories created"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Installing Web Dependencies"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Try system packages first (pre-built for RISC-V)
echo "→ Attempting to install system packages..."
if sudo apt install -y python3-fastapi python3-uvicorn python3-jinja2 python3-yaml 2>/dev/null; then
    echo "✅ System packages installed"
    DEPS_OK=1
else
    echo "⚠️  System packages not available, using pip..."
    DEPS_OK=0
fi

# If system packages failed, use pip with minimal requirements
if [ $DEPS_OK -eq 0 ]; then
    echo ""
    echo "→ Installing via pip (this may take a while on RISC-V)..."

    # Create minimal requirements
    cat > /tmp/requirements-web.txt << 'EOF'
fastapi
uvicorn[standard]
jinja2
pyyaml
websockets
python-multipart
click
EOF

    # Try with pip
    if pip3 install --break-system-packages -r /tmp/requirements-web.txt 2>/dev/null; then
        echo "✅ Pip packages installed"
    else
        echo "⚠️  Pip installation had issues, trying one by one..."

        # Install one by one, ignore errors
        for pkg in fastapi uvicorn jinja2 pyyaml websockets python-multipart click; do
            echo "  → Installing $pkg..."
            pip3 install --break-system-packages $pkg 2>/dev/null || echo "    ⚠️  $pkg failed (may already be installed)"
        done
    fi

    rm -f /tmp/requirements-web.txt
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📚 Installing Transformers (RISC-V compatible)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Install transformers without Rust dependencies
echo "→ Installing transformers 4.30.2 (no Rust deps)..."
if pip3 install --break-system-packages --no-deps "transformers==4.30.2" 2>/dev/null; then
    echo "✅ Transformers installed"
else
    echo "⚠️  Transformers installation had issues, trying alternative..."
    pip3 install --break-system-packages --no-cache-dir --no-deps "transformers==4.30.2" || echo "⚠️  May already be installed"
fi

# Install transformers compatible dependencies (no tokenizers/safetensors)
echo "→ Installing transformers dependencies..."
for dep in filelock huggingface-hub packaging pyyaml regex requests tqdm; do
    pip3 install --break-system-packages $dep 2>/dev/null || echo "  ⚠️  $dep may already be installed"
done

# Install pydantic v1 (v2 requires Rust)
echo "→ Installing pydantic v1..."
pip3 install --break-system-packages "pydantic<2.0" 2>/dev/null || echo "  ⚠️  Pydantic may already be installed"

echo "✅ Transformers setup complete"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎤 Installing PyAudio (for microphone input)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# PyAudio needs portaudio dev library
echo "→ Installing portaudio development files..."
if sudo apt install -y portaudio19-dev python3-dev 2>/dev/null; then
    echo "✅ Portaudio dev installed"
else
    echo "⚠️  Portaudio installation had issues"
fi

# Install PyAudio from source
echo "→ Installing PyAudio (building from source)..."
if pip3 install --break-system-packages --no-cache-dir pyaudio 2>/dev/null; then
    echo "✅ PyAudio installed"
else
    echo "⚠️  PyAudio installation failed - live recording may not work"
    echo "   You can still use the app for transcribing audio files"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Web App Dependencies"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test imports
echo "→ Testing Python imports..."
python3 << 'PYTEST'
import sys
errors = []

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
    import jinja2
    print("  ✅ jinja2")
except Exception as e:
    print(f"  ❌ jinja2: {e}")
    errors.append("jinja2")

try:
    import yaml
    print("  ✅ pyyaml")
except Exception as e:
    print(f"  ❌ pyyaml: {e}")
    errors.append("pyyaml")

try:
    import transformers
    print("  ✅ transformers")
except Exception as e:
    print(f"  ❌ transformers: {e}")
    errors.append("transformers")

try:
    import pydantic
    print("  ✅ pydantic")
except Exception as e:
    print(f"  ❌ pydantic: {e}")
    errors.append("pydantic")

try:
    import click
    print("  ✅ click (for CLI)")
except Exception as e:
    print(f"  ❌ click: {e}")
    errors.append("click")

try:
    import pyaudio
    print("  ✅ pyaudio (for microphone)")
except Exception as e:
    print(f"  ⚠️  pyaudio: {e} (optional - needed for live recording)")

if errors:
    print(f"\n⚠️  Some imports failed: {', '.join(errors)}")
    print("The app may still work with available packages")
else:
    print("\n✅ All core dependencies available!")
PYTEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📋 Next Steps:"
echo ""
echo "  1. Start the web app:"
echo "     python3 web_app.py"
echo ""
echo "  2. Open browser to:"
echo "     http://10.162.197.63:8000"
echo ""
echo "  3. Go to Settings page to test model switching:"
echo "     http://10.162.197.63:8000/settings"
echo ""
echo "💡 Tips:"
echo "  • Press Ctrl+C to stop the server"
echo "  • Check logs in logs/ directory"
echo "  • Config file: config.yaml"
echo ""
