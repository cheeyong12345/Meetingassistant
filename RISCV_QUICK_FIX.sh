#!/bin/bash
# Quick Fix Script for RISC-V Installation
# Handles packages that don't have RISC-V wheels

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         RISC-V Quick Fix - Install Compatible Versions       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not in virtual environment"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

echo "📦 Installing packages compatible with RISC-V..."
echo ""

# Use older versions that don't need Rust
echo "→ Installing Pydantic v1 (no Rust required)..."
pip install 'pydantic<2.0'

echo "→ Installing FastAPI with Pydantic v1..."
pip install 'fastapi[all]'

echo "→ Installing web framework..."
pip install uvicorn jinja2 python-multipart python-socketio

echo "→ Installing Transformers..."
pip install transformers

echo "→ Installing tokenizers (may take time)..."
pip install tokenizers

echo "→ Installing accelerate..."
pip install accelerate || echo "⚠️  Accelerate failed (optional)"

echo "→ Installing sentencepiece..."
pip install sentencepiece || echo "⚠️  SentencePiece failed (optional)"

echo "→ Installing protobuf..."
pip install protobuf

echo "→ Installing CLI tools..."
pip install click rich

echo "→ Installing utilities..."
pip install pyyaml requests aiofiles sqlalchemy python-dotenv

echo "→ Installing audio libraries..."
pip install pydub soundfile || echo "⚠️  Some audio libs failed (optional)"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Installation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verify
echo "📊 Verifying installation..."
python3 << 'EOF'
import sys

packages = {
    'numpy': 'NumPy',
    'scipy': 'SciPy',
    'transformers': 'Transformers',
    'fastapi': 'FastAPI',
    'pydantic': 'Pydantic',
    'uvicorn': 'Uvicorn',
    'click': 'Click',
    'yaml': 'PyYAML'
}

print("\nInstalled packages:")
all_ok = True
for module, name in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✓ {name:20s} {version}")
    except ImportError:
        print(f"  ✗ {name:20s} NOT INSTALLED")
        all_ok = False

if all_ok:
    print("\n✅ All critical packages installed successfully!")
else:
    print("\n⚠️  Some packages missing - but core should work")

sys.exit(0 if all_ok else 1)
EOF

echo ""
echo "📋 Next Steps:"
echo "  1. Test import: python3 -c 'import fastapi, transformers'"
echo "  2. Download models: python3 scripts/install_sbc.py --models-only"
echo "  3. Run web app: python3 web_app.py"
echo ""
