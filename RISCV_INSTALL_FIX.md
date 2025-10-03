# RISC-V Installation Fix - SciPy Fortran Compiler Error

## Quick Fix (Run This Now)

The error occurs because **SciPy needs a Fortran compiler** to build on RISC-V. Here's how to fix it:

### Step 1: Install Fortran Compiler and Math Libraries

```bash
sudo apt update
sudo apt install -y gfortran libopenblas-dev liblapack-dev libblas-dev
```

### Step 2: Install NumPy (Fast)

```bash
cd ~/Meetingassistant
source venv/bin/activate
pip install numpy
```

### Step 3: Install SciPy (Slow - 10-30 minutes)

```bash
# This will compile from source - be patient!
pip install scipy
```

**⏰ Note**: SciPy compilation takes 10-30 minutes on RISC-V. This is normal!

### Step 4: Continue Installation

```bash
# Now continue with the rest of the installation
python3 scripts/install_sbc.py --models-only
```

---

## Alternative: Skip SciPy (Faster, Core Features Still Work)

If you don't want to wait for SciPy compilation:

### Option 1: Install Without SciPy

```bash
cd ~/Meetingassistant
source venv/bin/activate

# Install all dependencies EXCEPT scipy
pip install numpy
pip install pyaudio pydub soundfile
pip install fastapi uvicorn jinja2 python-multipart python-socketio
pip install click rich
pip install python-dotenv requests aiofiles sqlalchemy pyyaml
pip install transformers accelerate sentencepiece protobuf
pip install onnxruntime

# Optional
pip install ollama
```

**✅ This works fine!** SciPy is only used for some advanced audio processing features that aren't critical.

---

## What Went Wrong?

**Problem**: On RISC-V, SciPy has no pre-built wheels, so it must be compiled from source.

**Requirements**: SciPy compilation needs:
- ✅ Fortran compiler (gfortran)
- ✅ BLAS library (libopenblas-dev)
- ✅ LAPACK library (liblapack-dev)

**Error**: The installation script tried to install SciPy before installing gfortran.

**Fix**: Updated script now installs gfortran first for RISC-V systems.

---

## Updated Installation Script

I've fixed the installation script. Pull the latest changes:

```bash
cd ~/Meetingassistant
git pull origin main
```

Then run:

```bash
python3 scripts/install_sbc.py
```

The updated script will:
1. ✅ Auto-detect RISC-V architecture
2. ✅ Install gfortran and math libraries first
3. ✅ Install NumPy separately
4. ✅ Give SciPy 1-hour timeout for compilation
5. ✅ Continue without SciPy if it fails
6. ✅ Show clear progress messages

---

## Manual Installation (Complete)

If you want full control, here's the complete manual installation:

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3-dev python3-pip python3-venv build-essential \
    cmake pkg-config gfortran libopenblas-dev liblapack-dev libblas-dev \
    libasound2-dev portaudio19-dev libportaudio2 libsndfile1-dev ffmpeg

# 2. Create virtual environment
cd ~/Meetingassistant
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install NumPy (5-10 minutes)
pip install numpy

# 5. Install SciPy (10-30 minutes) - OPTIONAL
pip install scipy

# 6. Install ONNX Runtime (IMPORTANT for NPU)
pip install onnxruntime

# 7. Install audio libraries
pip install pyaudio pydub soundfile

# 8. Install web framework
pip install fastapi uvicorn jinja2 python-multipart python-socketio

# 9. Install CLI tools
pip install click rich

# 10. Install utilities
pip install python-dotenv requests aiofiles sqlalchemy pyyaml

# 11. Install AI/ML (without PyTorch for now)
pip install transformers accelerate sentencepiece protobuf

# 12. Install optional packages
pip install ollama

# 13. Verify installation
python3 -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python3 -c "import onnxruntime; print(f'ONNX Runtime: {onnxruntime.__version__}')"
```

---

## Check What's Installed

```bash
source venv/bin/activate

# Check critical packages
python3 << 'EOF'
import sys
packages = [
    'numpy', 'scipy', 'onnxruntime', 'transformers',
    'fastapi', 'pyaudio', 'pydub'
]

for pkg in packages:
    try:
        mod = __import__(pkg)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✅ {pkg:20s} {version}")
    except ImportError:
        print(f"❌ {pkg:20s} NOT INSTALLED")
EOF
```

---

## Expected Build Times on RISC-V

| Package | Build Time | Required? |
|---------|------------|-----------|
| NumPy | 5-10 minutes | ✅ Yes |
| SciPy | 10-30 minutes | ⚠️ Optional |
| ONNX Runtime | Pre-built (instant) | ✅ Recommended |
| Transformers | Pre-built (instant) | ✅ Yes |
| PyTorch | 6-12 hours | ⚠️ Optional (use ONNX instead) |

---

## Why SciPy Takes So Long?

SciPy contains:
- 📊 Scientific computing algorithms
- 🧮 Linear algebra routines (calling Fortran BLAS/LAPACK)
- 📈 Statistical functions
- 🔢 Optimization algorithms

All of this must be **compiled from C/Fortran source code** on RISC-V.

**Good news**: You only need to compile it once!

---

## Summary

### Immediate Fix (Choose One):

**Option A: Install with SciPy (slow but complete)**
```bash
sudo apt install -y gfortran libopenblas-dev liblapack-dev libblas-dev
pip install numpy scipy  # Wait 10-30 minutes
```

**Option B: Install without SciPy (fast, works fine)**
```bash
pip install numpy  # Skip scipy
# Core features work without it!
```

### Long-term Fix:

Pull the updated installation script:
```bash
git pull origin main
python3 scripts/install_sbc.py
```

The script is now fixed to handle RISC-V properly! 🎉

---

## Need Help?

If you're still stuck:

1. Check what's failing:
```bash
pip install numpy --verbose
```

2. Verify gfortran is installed:
```bash
gfortran --version
```

3. Check build dependencies:
```bash
dpkg -l | grep -E "(gfortran|openblas|lapack)"
```

4. Try installing in debug mode:
```bash
pip install scipy --verbose --no-cache-dir
```
