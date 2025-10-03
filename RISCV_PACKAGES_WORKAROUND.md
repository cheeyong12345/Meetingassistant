# RISC-V Packages Workaround

## Problem

Several Python packages don't have pre-built wheels for RISC-V and require compilation with tools not available on RISC-V:

1. **ONNX Runtime** - No RISC-V wheels available
2. **PyTorch** - No RISC-V wheels available
3. **Pydantic v2** - Requires Rust compiler (rustup doesn't support RISC-V target)
4. **Tokenizers** - May require Rust

## Quick Solution

### Option 1: Use Bash Script (Fastest)

```bash
cd ~/Meetingassistant
source venv/bin/activate
bash RISCV_QUICK_FIX.sh
```

This script installs compatible versions automatically.

### Option 2: Manual Installation (More Control)

```bash
cd ~/Meetingassistant
source venv/bin/activate

# Use Pydantic v1 (no Rust required)
pip install 'pydantic<2.0'

# Install FastAPI with Pydantic v1
pip install 'fastapi[all]'

# Or install components separately
pip install fastapi uvicorn jinja2 python-multipart python-socketio

# Install Transformers
pip install transformers

# Install other packages
pip install click rich pyyaml requests aiofiles sqlalchemy python-dotenv

# Optional: audio libraries
pip install pydub soundfile
```

## Package Version Strategy

### ✅ Use These Versions on RISC-V

| Package | Version | Why |
|---------|---------|-----|
| **pydantic** | <2.0 | v2+ requires Rust (not available on RISC-V) |
| **fastapi** | latest | Works with Pydantic v1 |
| **transformers** | latest | Pure Python, no compilation needed |
| **numpy** | latest | Compiles successfully on RISC-V |
| **scipy** | latest | Compiles with gfortran (slow but works) |

### ❌ Skip These on RISC-V

| Package | Reason | Alternative |
|---------|--------|-------------|
| **onnxruntime** | No RISC-V wheels | Use Transformers CPU inference |
| **torch** | No RISC-V wheels | Use Transformers or build from source |
| **tokenizers** | May need Rust | Use slower Python tokenizers |

## Understanding the Issues

### Pydantic v2 / Rust Issue

**Error:**
```
Target triple not supported by rustup: riscv64-unknown-linux-gnu
Rust not found, installing into a temporary directory
```

**Cause:**
- Pydantic v2 uses `pydantic-core` (written in Rust)
- Rust's `rustup` doesn't have RISC-V target support yet
- Can't compile Rust extensions on RISC-V

**Solution:**
- Use Pydantic v1.x (pure Python)
- FastAPI works fine with Pydantic v1

### ONNX Runtime Issue

**Error:**
```
ERROR: Could not find a version that satisfies the requirement onnxruntime
```

**Cause:**
- No pre-built ONNX Runtime wheels for RISC-V
- Building from source is complex

**Solution:**
- Skip ONNX Runtime
- Use Hugging Face Transformers for inference (works great!)
- Or install ENNP SDK from ESWIN for NPU acceleration

### PyTorch Issue

**Error:**
```
ERROR: Could not find a version that satisfies the requirement torch
```

**Cause:**
- No pre-built PyTorch wheels for RISC-V
- Building from source takes 6-12 hours

**Solution:**
- Skip PyTorch for now
- Use Transformers library (doesn't require PyTorch for inference)
- Or build PyTorch from source if needed (see below)

## What Works Without ONNX/PyTorch?

### ✅ Full Functionality Available

The Meeting Assistant works completely without ONNX Runtime or PyTorch:

1. **Speech-to-Text**:
   - ✅ Whisper models via `openai-whisper` (uses own inference)
   - ✅ Vosk (lightweight offline STT)
   - ✅ Google Speech Recognition (API-based)

2. **Summarization**:
   - ✅ Transformers with CPU inference
   - ✅ Ollama (if installed separately)
   - ✅ OpenAI API (if API key provided)

3. **Web Interface**:
   - ✅ FastAPI + Uvicorn
   - ✅ WebSocket support
   - ✅ All UI features

4. **Audio Processing**:
   - ✅ PyAudio for recording
   - ✅ Pydub for manipulation
   - ✅ SoundFile for I/O

## Performance Impact

| Component | With ONNX/PyTorch | Without (Transformers only) | Impact |
|-----------|-------------------|----------------------------|--------|
| Whisper STT | Fast | Same (uses own engine) | None |
| Qwen Summarization | Fast | Slower (CPU only) | 2-3x slower |
| Web Interface | N/A | N/A | None |

**Reality**: Slightly slower AI inference, but fully functional!

## Building PyTorch from Source (Optional)

If you really need PyTorch:

```bash
# Install build dependencies (takes 1-2 hours)
sudo apt install -y cmake ninja-build git

# Clone PyTorch
git clone --recursive https://github.com/pytorch/pytorch
cd pytorch

# Configure for RISC-V
export USE_CUDA=0
export USE_MKLDNN=0
export USE_NNPACK=0
export BUILD_TEST=0

# Build (takes 6-12 hours!)
python3 setup.py install
```

**Recommendation**: Don't do this unless absolutely necessary. Transformers works fine without it.

## Testing Your Installation

### Verify Core Packages

```bash
python3 << 'EOF'
# Test imports
import numpy
import scipy
import transformers
import fastapi
import pydantic

print(f"✅ NumPy:        {numpy.__version__}")
print(f"✅ SciPy:        {scipy.__version__}")
print(f"✅ Transformers: {transformers.__version__}")
print(f"✅ FastAPI:      {fastapi.__version__}")
print(f"✅ Pydantic:     {pydantic.__version__}")

# Verify Pydantic version
assert pydantic.__version__.startswith('1.'), "Pydantic v2 detected - needs v1 for RISC-V"
print("\n✅ All packages compatible with RISC-V!")
EOF
```

### Test Transformers Inference

```bash
python3 << 'EOF'
from transformers import pipeline

print("Loading sentiment analysis model...")
classifier = pipeline("sentiment-analysis")

result = classifier("I love using RISC-V!")
print(f"✅ Result: {result}")
print("✅ Transformers inference working!")
EOF
```

## Summary

### What You Need to Do

1. **Use Pydantic v1** instead of v2
2. **Skip ONNX Runtime** (use Transformers instead)
3. **Skip PyTorch** (use Transformers instead)
4. **Everything else** installs normally

### Commands

```bash
cd ~/Meetingassistant
source venv/bin/activate

# Quick fix
bash RISCV_QUICK_FIX.sh

# Or manual
pip install 'pydantic<2.0' 'fastapi[all]' transformers click rich
```

### Expected Result

```
✅ NumPy         2.3.3
✅ SciPy         1.16.2
✅ Transformers  4.x.x
✅ FastAPI       0.x.x
✅ Pydantic      1.10.x  (NOT 2.x)
```

All functionality works, just slightly slower inference without GPU/NPU acceleration (which is expected on RISC-V).
