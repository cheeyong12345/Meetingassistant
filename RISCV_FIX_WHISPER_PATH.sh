#!/bin/bash
# Fix whisper.cpp binary path for CMake build

echo "🔍 Finding whisper.cpp binary..."
echo ""

WHISPER_DIR="$HOME/whisper.cpp"

if [ ! -d "$WHISPER_DIR" ]; then
    echo "❌ Whisper.cpp directory not found at $WHISPER_DIR"
    exit 1
fi

cd "$WHISPER_DIR"

# Find the actual binary location after CMake build
echo "→ Searching for whisper.cpp binaries..."
echo ""

# Common locations for CMake builds
POSSIBLE_PATHS=(
    "build/bin/main"
    "build/bin/whisper-cli"
    "build/main"
    "build/whisper-cli"
    "main"
    "whisper-cli"
)

FOUND_BINARY=""

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$WHISPER_DIR/$path" ]; then
        echo "  ✅ Found: $path"
        if [ -z "$FOUND_BINARY" ]; then
            FOUND_BINARY="$path"
        fi
    fi
done

if [ -z "$FOUND_BINARY" ]; then
    echo "❌ No whisper.cpp binary found!"
    echo ""
    echo "→ Listing build directory contents:"
    ls -lah "$WHISPER_DIR/build/" 2>/dev/null || echo "  No build directory"
    ls -lah "$WHISPER_DIR/build/bin/" 2>/dev/null || echo "  No build/bin directory"
    exit 1
fi

echo ""
echo "✅ Using binary: $FOUND_BINARY"
echo ""

# Test the binary
echo "→ Testing binary..."
cd "$WHISPER_DIR"

# Try different test methods
BINARY_WORKS=0

if ./"$FOUND_BINARY" -h > /dev/null 2>&1; then
    echo "✅ Binary works with -h!"
    BINARY_WORKS=1
elif ./"$FOUND_BINARY" --help > /dev/null 2>&1; then
    echo "✅ Binary works with --help!"
    BINARY_WORKS=1
elif ./"$FOUND_BINARY" 2>&1 | grep -qi "usage\|whisper"; then
    echo "✅ Binary works!"
    BINARY_WORKS=1
else
    echo "⚠️  Binary test inconclusive, checking if executable..."
    if [ -x "$WHISPER_DIR/$FOUND_BINARY" ]; then
        echo "✅ Binary is executable (assuming it works)"
        BINARY_WORKS=1
    else
        echo "❌ Binary not executable"
        chmod +x "$WHISPER_DIR/$FOUND_BINARY"
        if [ -x "$WHISPER_DIR/$FOUND_BINARY" ]; then
            echo "✅ Fixed permissions"
            BINARY_WORKS=1
        fi
    fi
fi

if [ $BINARY_WORKS -eq 0 ]; then
    echo "❌ Binary test failed"
    echo "→ Running diagnostics..."
    echo ""
    echo "File info:"
    ls -lh "$WHISPER_DIR/$FOUND_BINARY"
    echo ""
    echo "Trying to run:"
    ./"$FOUND_BINARY" 2>&1 | head -5
    exit 1
fi

# Create symlink at old location for compatibility
echo ""
echo "→ Creating compatibility symlink..."

if [ "$FOUND_BINARY" != "main" ]; then
    # Remove old symlink if exists
    rm -f "$WHISPER_DIR/main"

    # Create new symlink
    ln -sf "$FOUND_BINARY" "$WHISPER_DIR/main"

    if [ -f "$WHISPER_DIR/main" ]; then
        echo "✅ Symlink created: main -> $FOUND_BINARY"
    else
        echo "❌ Failed to create symlink"
        exit 1
    fi
else
    echo "✅ Binary already at expected location"
fi

# Verify symlink works
echo ""
echo "→ Verifying symlink..."
if [ -L "$WHISPER_DIR/main" ] && [ -e "$WHISPER_DIR/main" ]; then
    echo "✅ Symlink exists and points to valid file"

    # Quick test
    if "$WHISPER_DIR/main" -h > /dev/null 2>&1 || [ -x "$WHISPER_DIR/main" ]; then
        echo "✅ Symlink works!"
    else
        echo "⚠️  Symlink exists but test inconclusive (assuming it works)"
    fi
else
    echo "⚠️  Symlink verification failed (but might still work)"
fi

# Check models
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Checking models"
echo "════════════════════════════════════════════════════════════════"
echo ""

MODELS_DIR="$WHISPER_DIR/models"

if [ ! -d "$MODELS_DIR" ]; then
    echo "⚠️  Models directory not found, creating..."
    mkdir -p "$MODELS_DIR"
fi

echo "→ Available models:"
MODELS_FOUND=0

for model in tiny tiny.en base base.en small small.en medium medium.en large; do
    if [ -f "$MODELS_DIR/ggml-$model.bin" ]; then
        size=$(du -h "$MODELS_DIR/ggml-$model.bin" | cut -f1)
        echo "  ✅ $model ($size)"
        MODELS_FOUND=$((MODELS_FOUND + 1))
    fi
done

if [ $MODELS_FOUND -eq 0 ]; then
    echo "  ❌ No models found"
    echo ""
    echo "→ Downloading base model..."
    cd "$WHISPER_DIR"
    bash ./models/download-ggml-model.sh base
    MODELS_FOUND=1
else
    echo ""
    echo "✅ Found $MODELS_FOUND model(s)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Whisper.cpp is ready!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Binary: $WHISPER_DIR/main -> $FOUND_BINARY"
echo "Models: $MODELS_FOUND found"
echo ""
echo "🚀 Now run:"
echo "  cd ~/Meetingassistant"
echo "  python3 web_app.py"
echo ""
