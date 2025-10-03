# RISC-V Setup Guide - Meeting Assistant

Complete guide for running Meeting Assistant on RISC-V architecture (ESWIN EIC7700/EIC7700X).

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Storage Setup](#storage-setup)
- [Installation](#installation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)

---

## 🚀 Quick Start

### Prerequisites
- RISC-V device (ESWIN EIC7700/EIC7700X)
- Ubuntu/Debian-based OS
- At least 30GB available storage
- Internet connection

### One-Command Installation

```bash
cd ~/Meetingassistant

# 1. Expand storage (if needed)
sudo bash RISCV_EXPAND_EMMC.sh

# 2. Complete setup
bash RISCV_COMPLETE_SETUP.sh

# 3. Start application
source venv/bin/activate
python3 web_app.py
```

Open browser: http://localhost:8000

---

## 🏗️ Architecture Overview

### Hardware Stack
- **SoC**: ESWIN EIC7700 (4×C920 RISC-V cores @ 2.0GHz)
- **NPU**: ESWIN ENNP (13.3-19.95 TOPS)
- **Memory**: 8GB/16GB LPDDR4X
- **Storage**: eMMC 32GB/64GB

### Software Stack
```
┌─────────────────────────────────────┐
│         Web Interface               │
│      (FastAPI + Uvicorn)           │
├─────────────────────────────────────┤
│  STT              Summarization     │
│  Whisper.cpp      ESWIN NPU Qwen2  │
│  (C++ binary)     (NPU binary)     │
├─────────────────────────────────────┤
│     Python 3.10 (RISC-V)           │
│  Transformers (no PyTorch/Rust)    │
└─────────────────────────────────────┘
```

### Key Differences from x86/ARM
- **No PyTorch**: Use whisper.cpp instead of openai-whisper
- **No Rust**: Use older transformers version (4.30.2)
- **No ONNX Runtime**: CPU inference only
- **NPU Acceleration**: Via ESWIN binary for Qwen2 7B

---

## 💾 Storage Setup

### Check Current Storage

```bash
df -h /
lsblk
```

### Expand eMMC (if needed)

If your eMMC shows unallocated space:

```bash
sudo bash RISCV_EXPAND_EMMC.sh
```

**What it does:**
- Analyzes current partition layout
- Expands root partition to use full disk
- Resizes filesystem automatically
- Safe to run while system is online

**Example:**
```
Before: mmcblk0p2 = 28.4G (out of 58.2G total)
After:  mmcblk0p2 = 58.2G (full disk)
Gained: ~30GB additional space
```

---

## 📦 Installation

### Automated Installation

```bash
cd ~/Meetingassistant
bash RISCV_COMPLETE_SETUP.sh
```

**What it installs:**
1. **Whisper.cpp** - STT engine (C++ implementation, no PyTorch)
   - Builds from source
   - Downloads base model (150MB)
   - Binary: `~/whisper.cpp/build/bin/whisper-cli`

2. **Python Dependencies**
   - Transformers 4.30.2 (no Rust dependencies)
   - Pydantic v1 (Rust not available on RISC-V)
   - FastAPI + Uvicorn
   - Compatible versions only

3. **Configuration**
   - Creates optimized `config.yaml`
   - Sets whisper.cpp as default STT
   - Enables ESWIN NPU for summarization

### Manual Installation

See [RISCV_MANUAL_INSTALL.md](RISCV_MANUAL_INSTALL.md) for step-by-step guide.

---

## ⚙️ Configuration

### Main Config (config.yaml)

```yaml
# Speech-to-Text (Whisper.cpp)
stt:
  default_engine: whispercpp
  engines:
    whispercpp:
      model_size: base           # tiny, base, small, medium
      language: auto             # auto-detect or 'en', 'zh', etc.
      threads: 4                 # CPU threads

# Summarization (ESWIN NPU - Qwen2 7B)
summarization:
  default_engine: qwen
  engines:
    qwen:
      model_name: Qwen/Qwen2.5-3B-Instruct
      device: auto
      use_npu: true              # Use ESWIN NPU binary
      max_tokens: 1000
      temperature: 0.7
```

### Whisper.cpp Models

Available models (size vs accuracy):
- `tiny.en` - 75MB, English only, fastest
- `tiny` - 75MB, multilingual, fastest
- `base` - 150MB, good balance ✅ **recommended**
- `small` - 500MB, better accuracy
- `medium` - 1.5GB, high accuracy (needs 30GB+ storage)

Change model:
```bash
cd ~/whisper.cpp
bash ./models/download-ggml-model.sh small  # download
```

Update config.yaml:
```yaml
whispercpp:
  model_size: small
```

---

## 🐛 Troubleshooting

### Issue: No STT engine available

**Symptom:**
```
WARNING: No STT engines could be registered - STT features will be disabled
```

**Solution:**
```bash
# Reinstall whisper.cpp
cd ~
rm -rf whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make -j$(nproc)
bash ./models/download-ggml-model.sh base

# Verify
ls -lh ~/whisper.cpp/build/bin/whisper-cli
ls -lh ~/whisper.cpp/models/ggml-base.bin
```

### Issue: Disk full during installation

**Symptom:**
```
cp: error writing: No space left on device
```

**Solution:**
```bash
# Check space
df -h /

# Expand eMMC if unallocated space available
sudo bash RISCV_EXPAND_EMMC.sh

# Or clean up
pip cache purge
sudo apt clean
rm -rf ~/.cache/*
```

### Issue: Import errors (tokenizers, safetensors)

**Symptom:**
```
ModuleNotFoundError: No module named 'tokenizers'
```

**Cause:** Transformers too new, requires Rust (not available on RISC-V)

**Solution:**
```bash
# Install compatible version
pip uninstall transformers -y
pip install --no-cache-dir --no-deps "transformers==4.30.2"
pip install --no-cache-dir filelock huggingface-hub packaging pyyaml regex requests tqdm
```

### Issue: ESWIN NPU not detected

**Symptom:**
```
ESWIN NPU not detected (optional)
```

**Check NPU binary:**
```bash
ls -la /opt/eswin/sample-code/npu_sample/qwen_sample/bin/es_qwen2
```

**If missing:** NPU will fallback to CPU inference (slower but works)

### Issue: Whisper.cpp binary not found

**Symptom:**
```
FileNotFoundError: ~/whisper.cpp/build/bin/whisper-cli
```

**Solution:**
```bash
# Rebuild whisper.cpp
cd ~/whisper.cpp
make clean
make -j$(nproc)

# Verify binary
./build/bin/whisper-cli --help
```

---

## 🚫 Known Limitations

### Cannot Install on RISC-V
- ❌ PyTorch (no pre-built wheels)
- ❌ ONNX Runtime (no pre-built wheels)
- ❌ Pydantic v2 (requires Rust, rustup doesn't support riscv64)
- ❌ Tokenizers (requires Rust)
- ❌ Safetensors (requires Rust)

### Workarounds Used
- ✅ Whisper.cpp instead of openai-whisper (no PyTorch needed)
- ✅ Transformers 4.30.2 with `--no-deps` (avoids Rust)
- ✅ Pydantic v1 instead of v2 (no Rust needed)
- ✅ ESWIN NPU binary for Qwen2 (native acceleration)

### Performance Notes
- **STT**: Whisper.cpp on CPU is slower than GPU Whisper (~2-4x realtime)
- **Summarization**: NPU acceleration provides 3-5x speedup vs CPU
- **Best model for realtime**: base model with 4 threads

---

## 📂 File Structure

```
docs/riscv/
├── README.md                       # This file
├── HARDWARE_STACK.md              # ESWIN NPU integration details
├── RISCV_MANUAL_INSTALL.md        # Step-by-step manual guide
├── RISCV_PACKAGES_WORKAROUND.md   # Package compatibility details
├── RISCV_CONFIG_WHISPERCPP.yaml   # Example configuration
├── scripts/
│   ├── RISCV_COMPLETE_SETUP.sh    # Main installation script
│   └── RISCV_EXPAND_EMMC.sh       # Storage expansion script
└── archive/
    └── [older scripts]            # Historical/deprecated scripts
```

---

## 🔗 Useful Links

- [Whisper.cpp Repository](https://github.com/ggerganov/whisper.cpp)
- [ESWIN Developer Portal](https://www.eswincomputing.com)
- [Transformers Documentation](https://huggingface.co/docs/transformers)

---

## 📝 Quick Reference Commands

```bash
# Check system info
uname -m                    # Should show: riscv64
lscpu                       # CPU details
df -h /                     # Disk usage

# Installation
bash RISCV_COMPLETE_SETUP.sh

# Start app
cd ~/Meetingassistant
source venv/bin/activate
python3 web_app.py

# Test whisper.cpp
~/whisper.cpp/build/bin/whisper-cli \
  -m ~/whisper.cpp/models/ggml-base.bin \
  -f audio.wav

# Check logs
tail -f ~/Meetingassistant/logs/app.log

# Clean up space
pip cache purge
sudo apt clean
rm -rf ~/.cache/*
```

---

## 🆘 Support

For issues specific to:
- **RISC-V architecture**: Check [RISCV_PACKAGES_WORKAROUND.md](RISCV_PACKAGES_WORKAROUND.md)
- **ESWIN NPU**: See [HARDWARE_STACK.md](HARDWARE_STACK.md)
- **Whisper.cpp**: Visit [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp/issues)
- **General app issues**: Main [README.md](../../README.md)

---

**Last Updated**: 2025-10-03
**Platform**: RISC-V (ESWIN EIC7700)
**Tested On**: Ubuntu 22.04 RISC-V
