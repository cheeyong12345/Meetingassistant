#!/bin/bash
# Check and fix whisper.cpp installation for RISC-V

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║      Check & Fix Whisper.cpp Installation (RISC-V)          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

WHISPER_DIR="$HOME/whisper.cpp"

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Checking whisper.cpp installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if whisper.cpp directory exists
if [ ! -d "$WHISPER_DIR" ]; then
    echo "❌ Whisper.cpp directory not found at $WHISPER_DIR"
    echo "→ Cloning whisper.cpp..."

    cd ~
    git clone https://github.com/ggerganov/whisper.cpp.git

    if [ ! -d "$WHISPER_DIR" ]; then
        echo "❌ Failed to clone whisper.cpp"
        exit 1
    fi

    echo "✅ Whisper.cpp cloned successfully"
else
    echo "✅ Whisper.cpp directory exists: $WHISPER_DIR"
fi

# Check if binary exists
if [ ! -f "$WHISPER_DIR/main" ]; then
    echo "❌ Whisper.cpp binary not found at $WHISPER_DIR/main"
    echo "→ Building whisper.cpp..."

    cd "$WHISPER_DIR"

    # Build with optimizations for RISC-V
    make clean 2>/dev/null || true
    make -j$(nproc)

    if [ ! -f "$WHISPER_DIR/main" ]; then
        echo "❌ Build failed - main binary not created"
        echo "→ Trying alternative build method..."

        # Try with explicit compiler flags
        make clean
        CFLAGS="-O3 -march=native" CXXFLAGS="-O3 -march=native" make -j$(nproc)

        if [ ! -f "$WHISPER_DIR/main" ]; then
            echo "❌ Build still failed"
            exit 1
        fi
    fi

    echo "✅ Whisper.cpp binary built successfully"
else
    echo "✅ Whisper.cpp binary exists: $WHISPER_DIR/main"
fi

# Test binary
echo ""
echo "→ Testing whisper.cpp binary..."
if $WHISPER_DIR/main -h > /dev/null 2>&1; then
    echo "✅ Whisper.cpp binary works"
else
    echo "❌ Whisper.cpp binary test failed"
    exit 1
fi

# Check models directory
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Checking whisper models"
echo "════════════════════════════════════════════════════════════════"
echo ""

MODELS_DIR="$WHISPER_DIR/models"
mkdir -p "$MODELS_DIR"

# Check for downloaded models
echo "→ Scanning for downloaded models..."
MODELS_FOUND=0

for model in tiny tiny.en base base.en small small.en medium medium.en large; do
    if [ -f "$MODELS_DIR/ggml-$model.bin" ]; then
        size=$(du -h "$MODELS_DIR/ggml-$model.bin" | cut -f1)
        echo "  ✅ $model ($size)"
        MODELS_FOUND=$((MODELS_FOUND + 1))
    fi
done

if [ $MODELS_FOUND -eq 0 ]; then
    echo ""
    echo "❌ No models found"
    echo "→ Downloading base model (required)..."

    cd "$WHISPER_DIR"
    bash ./models/download-ggml-model.sh base

    if [ ! -f "$MODELS_DIR/ggml-base.bin" ]; then
        echo "❌ Failed to download base model"
        exit 1
    fi

    echo "✅ Base model downloaded"
    MODELS_FOUND=1
else
    echo ""
    echo "✅ Found $MODELS_FOUND model(s)"
fi

# Check if base or medium model exists (required for config)
if [ -f "$MODELS_DIR/ggml-base.bin" ]; then
    DEFAULT_MODEL="base"
    echo "→ Using 'base' as default model"
elif [ -f "$MODELS_DIR/ggml-medium.bin" ]; then
    DEFAULT_MODEL="medium"
    echo "→ Using 'medium' as default model"
elif [ -f "$MODELS_DIR/ggml-small.bin" ]; then
    DEFAULT_MODEL="small"
    echo "→ Using 'small' as default model"
else
    # Use first found model
    for model in tiny tiny.en base.en small.en medium.en large; do
        if [ -f "$MODELS_DIR/ggml-$model.bin" ]; then
            DEFAULT_MODEL="$model"
            echo "→ Using '$model' as default model"
            break
        fi
    done
fi

# Update config.yaml with correct model
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "⚙️  Updating config.yaml"
echo "════════════════════════════════════════════════════════════════"
echo ""

cd ~/Meetingassistant

if [ -f "config.yaml" ]; then
    # Check if model_size is set correctly
    if grep -q "model_size:" config.yaml; then
        # Update existing model_size
        sed -i "s/model_size: .*/model_size: \"$DEFAULT_MODEL\"/" config.yaml
        echo "✅ Updated model_size to: $DEFAULT_MODEL"
    else
        echo "⚠️  model_size not found in config.yaml"
    fi
else
    echo "⚠️  config.yaml not found"
fi

# Final verification
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Installation Check Complete"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📋 Summary:"
echo "  • Whisper.cpp: $WHISPER_DIR"
echo "  • Binary: $WHISPER_DIR/main"
echo "  • Models: $MODELS_FOUND found"
echo "  • Default model: $DEFAULT_MODEL"
echo ""

echo "🚀 Next Steps:"
echo "  1. Start the web app:"
echo "     cd ~/Meetingassistant"
echo "     python3 web_app.py"
echo ""
echo "  2. Access the web interface at:"
echo "     http://YOUR_IP:8001"
echo ""

echo "💡 To download more models:"
echo "  cd ~/whisper.cpp"
echo "  bash ./models/download-ggml-model.sh tiny     # Fastest, least accurate"
echo "  bash ./models/download-ggml-model.sh small    # Good balance"
echo "  bash ./models/download-ggml-model.sh medium   # Better accuracy"
echo "  bash ./models/download-ggml-model.sh large    # Best accuracy (slow)"
echo ""
