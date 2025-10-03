#!/bin/bash
# Quick one-liner installation for RISC-V
# Run this if RISCV_QUICK_FIX.sh doesn't work

echo "🚀 RISC-V Quick Install - Critical Packages Only"
echo ""

# Check venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Not in virtual environment!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Install system dependencies
echo "→ Installing libffi-dev..."
sudo apt install -y libffi-dev

# Install critical Python packages (no Rust dependencies)
echo ""
echo "→ Installing Python packages..."

# Pydantic v1 (not v2)
pip install --no-cache-dir "pydantic<2.0"

# Web framework
pip install --no-cache-dir fastapi uvicorn jinja2 python-multipart python-socketio

# Transformers WITHOUT tokenizers (to avoid Rust)
pip install --no-cache-dir --no-deps transformers
pip install --no-cache-dir filelock huggingface-hub packaging regex requests tqdm numpy

# CLI and utilities
pip install --no-cache-dir click rich pyyaml aiofiles sqlalchemy python-dotenv

# Audio (optional)
pip install --no-cache-dir pydub soundfile || echo "⚠️ Audio libraries failed (optional)"

# SentencePiece (may take time to compile)
pip install --no-cache-dir sentencepiece || echo "⚠️ SentencePiece failed (optional)"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Verify:"
python3 -c "import fastapi, uvicorn, transformers, pydantic; print('✅ All critical packages OK')"

echo ""
echo "Note: Using slow Python tokenizers (no Rust tokenizers installed)"
echo "This is normal and expected on RISC-V."
