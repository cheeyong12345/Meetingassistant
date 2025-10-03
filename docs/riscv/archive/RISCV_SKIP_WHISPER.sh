#!/bin/bash
# Make whisper optional - run app with ESWIN NPU only

echo "🔧 Making Whisper optional for RISC-V..."
echo ""

# Check venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Not in virtual environment!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Create a dummy whisper module to satisfy imports
SITE_PACKAGES=$(python3 -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])")
WHISPER_DIR="$SITE_PACKAGES/whisper"

if [ -d "$WHISPER_DIR" ]; then
    echo "✅ Whisper already installed (or dummy exists)"
else
    echo "→ Creating dummy whisper module..."
    mkdir -p "$WHISPER_DIR"

    # Create __init__.py
    cat > "$WHISPER_DIR/__init__.py" << 'EOF'
"""
Dummy whisper module for RISC-V (PyTorch not available)
The actual STT will use alternative methods or be disabled.
"""

class DummyWhisper:
    """Placeholder for whisper when PyTorch is not available"""
    pass

def load_model(name):
    """Dummy load_model function"""
    raise ImportError("Whisper requires PyTorch which is not available on RISC-V. Use alternative STT or disable STT.")

__version__ = "dummy-riscv"
EOF

    echo "  ✅ Dummy whisper module created at: $WHISPER_DIR"
fi

echo ""
echo "🧪 Testing imports..."
python3 << 'EOF'
import sys

# Test whisper import (should work with dummy)
try:
    import whisper
    print(f"  ✅ whisper module available (version: {whisper.__version__})")
except Exception as e:
    print(f"  ❌ whisper: {e}")
    sys.exit(1)

# Test other imports
try:
    import transformers
    print(f"  ✅ transformers {transformers.__version__}")
except Exception as e:
    print(f"  ❌ transformers: {e}")
    sys.exit(1)

try:
    import fastapi, uvicorn
    print(f"  ✅ fastapi {fastapi.__version__}")
    print(f"  ✅ uvicorn {uvicorn.__version__}")
except Exception as e:
    print(f"  ❌ web framework: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Import test failed"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ WHISPER MADE OPTIONAL"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 What This Does:"
echo "  • Creates a dummy whisper module to satisfy imports"
echo "  • web_app.py will now start without errors"
echo "  • STT features will be disabled or use alternative"
echo "  • Summarization works via ESWIN NPU (Qwen2 7B)"
echo ""
echo "📋 Next Steps:"
echo "  1. Start web app:"
echo "     python3 web_app.py"
echo ""
echo "  2. Open browser:"
echo "     http://localhost:8000"
echo ""
echo "  3. Use the summarization feature with ESWIN NPU"
echo ""
echo "⚠️  Note: Speech-to-text will be disabled"
echo "   You can paste text directly for summarization"
echo ""
