# RISC-V Manual Installation Guide

## For EIC7700 / EIC7700X RISC-V Platform

**Quick Summary**: Run the automated script OR follow manual steps below.

---

## Option 1: Automated Installation (Recommended)

```bash
cd ~/Meetingassistant
source venv/bin/activate
bash RISCV_QUICK_FIX.sh
```

The script will:
- ✅ Install all compatible packages
- ✅ Log detailed errors to `/tmp/riscv_install_*.log`
- ✅ Show clear success/failure summary
- ✅ Verify imports after installation

**Time**: 5-10 minutes

---

## Option 2: Manual Step-by-Step

### Step 1: Prepare Environment

```bash
cd ~/Meetingassistant

# Create virtual environment if not exists
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Step 2: Install System Dependencies (One-time)

```bash
sudo apt update
sudo apt install -y \
    python3-dev \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    libasound2-dev \
    portaudio19-dev \
    libsndfile1-dev \
    ffmpeg
```

### Step 3: Install NumPy and SciPy (Takes time on RISC-V)

```bash
# NumPy (5-10 minutes to compile)
pip install numpy

# SciPy (10-30 minutes - OPTIONAL, can skip)
pip install scipy
```

**Note**: SciPy compilation is slow but only needed once. You can skip it if you want faster installation.

### Step 4: Install Web Framework (CRITICAL)

```bash
# Install Pydantic v1 (v2 needs Rust which doesn't support RISC-V)
pip install 'pydantic<2.0'

# Install FastAPI and web components
pip install fastapi uvicorn jinja2 python-multipart python-socketio
```

**IMPORTANT**: Must use Pydantic < 2.0 for RISC-V!

### Step 5: Install AI/ML Libraries (CRITICAL)

```bash
# Transformers (Hugging Face)
pip install transformers

# Optional but recommended
pip install tokenizers sentencepiece protobuf accelerate
```

**Note**: Skip `onnxruntime` and `torch` - no RISC-V wheels available. We use Transformers' CPU inference instead.

### Step 6: Install Utilities

```bash
pip install \
    click \
    rich \
    pyyaml \
    requests \
    aiofiles \
    sqlalchemy \
    python-dotenv
```

### Step 7: Install Audio Libraries (OPTIONAL)

```bash
# May require compilation
pip install pydub soundfile

# If PyAudio not installed yet
pip install pyaudio
```

### Step 8: Verify Installation

```bash
python3 << 'EOF'
import numpy
import transformers
import fastapi
import pydantic
import uvicorn

print(f"✅ NumPy:        {numpy.__version__}")
print(f"✅ Transformers: {transformers.__version__}")
print(f"✅ FastAPI:      {fastapi.__version__}")
print(f"✅ Pydantic:     {pydantic.__version__}")
print(f"✅ Uvicorn:      {uvicorn.__version__}")

# Check Pydantic version
assert pydantic.__version__.startswith('1.'), "ERROR: Pydantic v2 detected (needs v1 for RISC-V)"

print("\n✅ All critical packages installed!")
EOF
```

---

## Troubleshooting

### Issue: `pip install` fails with "no matching distribution"

**Solution**: Package not available for RISC-V. Skip it or find alternative.

Common packages without RISC-V wheels:
- ❌ `torch` - Skip (use Transformers instead)
- ❌ `onnxruntime` - Skip (use Transformers CPU inference)
- ❌ `pydantic>=2.0` - Use `pydantic<2.0`

### Issue: SciPy compilation fails

```bash
# Install Fortran compiler and math libraries
sudo apt install -y gfortran libopenblas-dev liblapack-dev libblas-dev

# Try again
pip install scipy
```

### Issue: "Pydantic v2 requires Rust"

```bash
# Uninstall v2 and install v1
pip uninstall pydantic pydantic-core
pip install 'pydantic<2.0'
```

### Issue: Transformers import fails

```bash
# Install dependencies first
pip install numpy requests pyyaml
pip install filelock regex tqdm

# Then install transformers
pip install transformers
```

### Issue: "Permission denied" when installing system packages

```bash
# Make sure you have sudo access
sudo -v

# If you don't have sudo, ask system admin to install:
# gfortran libopenblas-dev liblapack-dev libasound2-dev portaudio19-dev
```

---

## What Gets Installed?

### Critical (Required for app to work):
- ✅ NumPy - Numerical computing
- ✅ Transformers - AI/ML models
- ✅ FastAPI - Web framework
- ✅ Pydantic v1 - Data validation (v1 only!)
- ✅ Uvicorn - ASGI server
- ✅ Click, Rich - CLI tools

### Optional (Enhances functionality):
- ⚠️ SciPy - Advanced math (slow to compile)
- ⚠️ Tokenizers - Fast tokenization (may need compilation)
- ⚠️ SentencePiece - Tokenization
- ⚠️ Accelerate - Hugging Face accelerator
- ⚠️ Pydub, SoundFile - Audio processing

### Not Available (Skip these):
- ❌ PyTorch - No RISC-V wheels (use Transformers instead)
- ❌ ONNX Runtime - No RISC-V wheels (use Transformers CPU)
- ❌ Pydantic v2+ - Requires Rust (use v1 instead)

---

## Expected Build Times

| Package | Time | Required? |
|---------|------|-----------|
| pip upgrade | 1 min | ✅ Yes |
| NumPy | 5-10 min | ✅ Yes |
| SciPy | 10-30 min | ⚠️ Optional |
| Transformers | 1-2 min | ✅ Yes |
| FastAPI | 1 min | ✅ Yes |
| Other packages | 2-5 min | ✅ Yes |
| **Total (with SciPy)** | **20-50 min** | |
| **Total (skip SciPy)** | **10-20 min** | |

---

## Quick Test After Installation

```bash
# Test web app imports
python3 -c "from src.meeting import MeetingAssistant; print('✅ Meeting Assistant imports OK')"

# Test FastAPI
python3 -c "import fastapi, uvicorn; print('✅ Web framework OK')"

# Test Transformers
python3 -c "import transformers; print('✅ AI/ML OK')"

# Check Pydantic version
python3 -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
```

All tests should print ✅ messages.

---

## Next Steps After Installation

1. **Clone/Update repository** (if not done):
   ```bash
   cd ~
   git clone https://github.com/cheeyong12345/Meetingassistant.git
   cd Meetingassistant
   ```

2. **Download AI models** (optional, can be done on-demand):
   ```bash
   source venv/bin/activate
   python3 scripts/install_sbc.py --models-only
   ```

3. **Configure for your hardware**:
   ```bash
   # Edit config.yaml
   nano config.yaml

   # Set:
   # - Audio device IDs
   # - Model paths
   # - Enable/disable NPU acceleration
   ```

4. **Run the web application**:
   ```bash
   source venv/bin/activate
   python3 web_app.py

   # Open browser: http://<your-ip>:8000
   ```

5. **For debugging** (if issues occur):
   ```bash
   cd debug
   python3 run_debug.py

   # Logs saved to: logs/debug_YYYYMMDD_HHMMSS.log
   ```

---

## Performance Notes for RISC-V

### CPU Inference (What we're using):
- Whisper `tiny`: ~2-3x realtime
- Whisper `base`: ~1-1.5x realtime
- Qwen 0.5B: ~5-10 tokens/sec

### NPU Acceleration (If ENNP SDK installed):
- Whisper `tiny`: ~10-15x realtime
- Whisper `base`: ~5-8x realtime
- Qwen 0.5B: ~20-50 tokens/sec

**To enable NPU**: See `docs/RISCV_DEPLOYMENT.md` for ENNP SDK installation.

---

## Getting Help

### Check Installation Logs

```bash
# If using automated script
cat /tmp/riscv_install_*.log

# Check recent pip errors
pip list --format=freeze | grep -E "(transformers|fastapi|pydantic)"
```

### Test Individual Packages

```bash
# Test if package can be imported
python3 -c "import transformers; print(transformers.__version__)"

# Install with verbose output
pip install transformers --verbose
```

### Common Issues Reference

See `RISCV_PACKAGES_WORKAROUND.md` for comprehensive troubleshooting.

---

## Summary Commands

```bash
# Full automated installation
cd ~/Meetingassistant
source venv/bin/activate
bash RISCV_QUICK_FIX.sh

# Or minimal critical packages only
pip install 'pydantic<2.0' fastapi uvicorn transformers click rich pyyaml

# Verify
python3 -c "from src.meeting import MeetingAssistant; print('OK')"

# Run app
python3 web_app.py
```

Done! 🎉
