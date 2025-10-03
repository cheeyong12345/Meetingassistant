#!/bin/bash
# Install Vosk STT engine for RISC-V (doesn't need PyTorch)

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         Installing Vosk STT for RISC-V                       ║"
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
echo "📦 Installing Vosk Python package"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Install vosk
pip install --no-cache-dir vosk

if [ $? -ne 0 ]; then
    echo "❌ Vosk installation failed"
    exit 1
fi

echo ""
echo "✅ Vosk installed successfully"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📥 Downloading Vosk English model (small, ~40MB)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create models directory
mkdir -p models/vosk

# Download small English model
cd models/vosk

if [ -d "vosk-model-small-en-us-0.15" ]; then
    echo "✅ Model already exists"
else
    echo "→ Downloading vosk-model-small-en-us-0.15..."
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

    if [ $? -ne 0 ]; then
        echo "❌ Download failed"
        exit 1
    fi

    echo "→ Extracting model..."
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip

    echo "✅ Model downloaded and extracted"
fi

cd ../..

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⚙️  Updating config.yaml"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Update config.yaml to use Vosk as default
python3 << 'EOF'
import yaml
from pathlib import Path

config_file = Path("config.yaml")
if config_file.exists():
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Set Vosk as default STT engine
    if 'stt' in config:
        config['stt']['default_engine'] = 'vosk'

        # Ensure vosk config exists
        if 'engines' not in config['stt']:
            config['stt']['engines'] = {}

        if 'vosk' not in config['stt']['engines']:
            config['stt']['engines']['vosk'] = {}

        # Set model path
        config['stt']['engines']['vosk']['model_path'] = 'models/vosk/vosk-model-small-en-us-0.15'
        config['stt']['engines']['vosk']['sample_rate'] = 16000

        # Write back
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        print("✅ Updated config.yaml to use Vosk")
    else:
        print("⚠️  No 'stt' section in config.yaml - manual update needed")
else:
    print("⚠️  config.yaml not found - manual configuration needed")
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Vosk Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 << 'EOF'
import sys

# Test vosk import
try:
    import vosk
    print(f"  ✅ vosk module available")
except Exception as e:
    print(f"  ❌ vosk import failed: {e}")
    sys.exit(1)

# Test model loading
try:
    import os
    model_path = "models/vosk/vosk-model-small-en-us-0.15"
    if os.path.exists(model_path):
        model = vosk.Model(model_path)
        print(f"  ✅ Vosk model loaded successfully")
        print(f"     Model path: {model_path}")
    else:
        print(f"  ❌ Model not found at {model_path}")
        sys.exit(1)
except Exception as e:
    print(f"  ❌ Model loading failed: {e}")
    sys.exit(1)

# Test STT engine
sys.path.insert(0, '.')
try:
    from src.stt.vosk_engine import VoskEngine
    print(f"  ✅ VoskEngine imports successfully")
except Exception as e:
    print(f"  ⚠️  VoskEngine import issue: {e}")

print("\n✅ Vosk installation complete!")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Vosk test failed"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ VOSK STT INSTALLED SUCCESSFULLY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 What's Installed:"
echo "  ✅ vosk Python package"
echo "  ✅ vosk-model-small-en-us-0.15 (English, ~40MB)"
echo "  ✅ config.yaml updated to use Vosk as default"
echo ""
echo "📋 STT Engine Details:"
echo "  • Engine: Vosk"
echo "  • Language: English"
echo "  • Size: Small (~40MB)"
echo "  • Accuracy: Good for most use cases"
echo "  • Speed: Fast (no GPU/NPU needed)"
echo "  • Requirements: No PyTorch needed!"
echo ""
echo "📋 Next Steps:"
echo "  1. Start web app:"
echo "     python3 web_app.py"
echo ""
echo "  2. Open browser:"
echo "     http://localhost:8000"
echo ""
echo "  3. Click 'Start Meeting' and speak!"
echo ""
echo "ℹ️  Note: For better accuracy, download larger model:"
echo "   • vosk-model-en-us-0.22 (~1.8GB)"
echo "   • vosk-model-en-us-0.22-lgraph (~128MB)"
echo ""
