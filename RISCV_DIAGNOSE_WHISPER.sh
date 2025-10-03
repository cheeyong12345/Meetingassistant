#!/bin/bash
# Diagnose whisper.cpp binary issues

echo "🔍 Diagnosing whisper.cpp binary..."
echo ""

WHISPER_DIR="$HOME/whisper.cpp"

cd "$WHISPER_DIR" || exit 1

# Find the binary
BINARY=""
if [ -f "build/bin/main" ]; then
    BINARY="build/bin/main"
elif [ -f "build/bin/whisper-cli" ]; then
    BINARY="build/bin/whisper-cli"
else
    echo "❌ No binary found"
    exit 1
fi

echo "Binary: $BINARY"
echo ""

# Check file info
echo "→ File info:"
ls -lh "$BINARY"
echo ""

# Check if executable
if [ -x "$BINARY" ]; then
    echo "✅ Binary is executable"
else
    echo "❌ Binary not executable, fixing..."
    chmod +x "$BINARY"
fi
echo ""

# Check library dependencies
echo "→ Library dependencies:"
ldd "$BINARY" 2>&1 | head -20
echo ""

# Try running with help
echo "→ Testing with --help:"
./"$BINARY" --help 2>&1 | head -10
echo ""

# Try running with -h
echo "→ Testing with -h:"
./"$BINARY" -h 2>&1 | head -10
echo ""

# Try running without args
echo "→ Testing without args:"
./"$BINARY" 2>&1 | head -10
echo ""

# Check which binary works
echo "════════════════════════════════════════════════════════════════"
if ./"$BINARY" -h > /dev/null 2>&1; then
    echo "✅ Binary works with -h flag"
elif ./"$BINARY" --help > /dev/null 2>&1; then
    echo "✅ Binary works with --help flag"
elif ./"$BINARY" 2>&1 | grep -q "usage"; then
    echo "✅ Binary works without args"
else
    echo "⚠️  Binary runs but might need specific arguments"
fi
echo ""
