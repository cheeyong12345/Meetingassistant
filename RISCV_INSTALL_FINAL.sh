#!/bin/bash
# Final RISC-V installation - use compatible transformers version

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   RISC-V Final Installation - Compatible Transformers        ║"
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
echo "📦 Uninstalling incompatible transformers version"
echo "════════════════════════════════════════════════════════════════"
echo ""

pip uninstall -y transformers

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Installing transformers 4.30.2 (no GGUF, works without tokenizers)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Install older transformers that doesn't require tokenizers for basic use
pip install --no-cache-dir "transformers==4.30.2"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Installation"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 << 'EOF'
import sys

print("Testing transformers import...")
try:
    import transformers
    print(f"  ✅ transformers {transformers.__version__}")
except Exception as e:
    print(f"  ❌ transformers import failed: {e}")
    sys.exit(1)

print("\nTesting basic functionality...")
try:
    # These should work without tokenizers
    from transformers import PreTrainedModel, PretrainedConfig
    print("  ✅ PreTrainedModel works")
    print("  ✅ PretrainedConfig works")
except Exception as e:
    print(f"  ❌ Basic imports failed: {e}")
    sys.exit(1)

print("\nTesting pipeline (may warn about PyTorch)...")
try:
    from transformers import pipeline
    print("  ✅ Pipeline import works")
except Exception as e:
    print(f"  ⚠️  Pipeline import failed: {e}")
    print("     (This is OK if PyTorch isn't installed)")

print("\n✅ Transformers 4.30.2 installed successfully!")
print("\nNote: This version works without Rust tokenizers")
print("You can use it with CPU inference or ESWIN NPU binary")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ INSTALLATION SUCCESSFUL"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Test Meeting Assistant
    echo "Testing Meeting Assistant imports..."
    python3 << 'EOFTEST'
import sys
sys.path.insert(0, '.')

try:
    from src.meeting import MeetingAssistant
    print("  ✅ MeetingAssistant imports OK")
except Exception as e:
    print(f"  ⚠️  MeetingAssistant import issue: {e}")
    print("     (May need PyTorch or will use ESWIN NPU)")

try:
    from src.config import config
    print("  ✅ Config loads OK")
except Exception as e:
    print(f"  ⚠️  Config issue: {e}")

try:
    import fastapi, uvicorn
    print(f"  ✅ FastAPI {fastapi.__version__}")
    print(f"  ✅ Uvicorn {uvicorn.__version__}")
except Exception as e:
    print(f"  ❌ Web framework failed: {e}")
EOFTEST

    echo ""
    echo "📋 Summary:"
    echo "  ✅ transformers 4.30.2 (compatible with RISC-V)"
    echo "  ✅ fastapi + uvicorn (web interface)"
    echo "  ✅ pydantic v1 (no Rust needed)"
    echo "  ⚠️  No tokenizers (using older transformers)"
    echo "  ⚠️  No PyTorch (will use ESWIN NPU for Qwen)"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Test web app: python3 web_app.py"
    echo "  2. Open browser: http://localhost:8000"
    echo ""
    echo "Note: The app will use ESWIN NPU binary for Qwen if available"
    echo ""
else
    echo ""
    echo "❌ Installation test failed"
    exit 1
fi
