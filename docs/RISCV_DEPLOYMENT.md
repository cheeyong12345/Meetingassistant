# RISC-V Deployment Guide

Complete guide for deploying Meeting Assistant on RISC-V platforms, specifically optimized for ESWIN EIC7700 SoC.

## Table of Contents
- [Hardware Overview](#hardware-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [NPU Acceleration](#npu-acceleration)
- [Model Conversion](#model-conversion)
- [Performance Optimization](#performance-optimization)
- [Benchmarking](#benchmarking)
- [Troubleshooting](#troubleshooting)

---

## Hardware Overview

### ESWIN EIC7700 Specifications

The EIC7700 is a high-performance RISC-V SoC designed for AI edge computing:

- **CPU**: RISC-V 64-bit multi-core processor
- **NPU**: ENNP (ESWIN Neural Network Processor)
  - **EIC7700**: 13.3 TOPS INT8
  - **EIC7700X**: 19.95 TOPS INT8
- **Memory**: Up to 16GB LPDDR4X
- **AI Framework Support**: ONNX Runtime, TensorFlow Lite, PyTorch (via build)

### Key Advantages

- ✅ High NPU performance (13-20 TOPS)
- ✅ Power efficient for edge AI
- ✅ Open RISC-V architecture
- ✅ ONNX Runtime support with ENNP Execution Provider

---

## Prerequisites

### Hardware Requirements

- **ESWIN EIC7700 or EIC7700X** development board
- **Minimum 8GB RAM** (16GB recommended)
- **32GB+ storage** (for models and datasets)
- **USB microphone** or audio input device
- **Network connection** for model downloads

### Software Requirements

- **OS**: Ubuntu 22.04+ (RISC-V port)
- **Python**: 3.10+
- **Git**: For cloning repository
- **Build tools**: gcc, cmake, make

---

## Installation

### 1. Quick Installation

The installation script automatically detects RISC-V and configures appropriately:

```bash
# Clone repository
git clone https://github.com/yourusername/meeting-assistant.git
cd meeting-assistant

# Run installation script
python3 scripts/install_sbc.py
```

### 2. Installation Options

When prompted for PyTorch installation, you have three options:

#### Option 1: Build from Source (6-12 hours)
```bash
Choose option [1-3] (default: 2): 1
```
- Compiles PyTorch natively for RISC-V
- Full PyTorch functionality
- Very time-consuming
- Requires 8GB+ RAM

#### Option 2: ONNX Runtime (Recommended) ⭐
```bash
Choose option [1-3] (default: 2): 2
```
- Fast installation
- Optimized for NPU via ENNP Execution Provider
- Best performance on EIC7700
- **Recommended for production use**

#### Option 3: Skip PyTorch
```bash
Choose option [1-3] (default: 2): 3
```
- Minimal installation
- ONNX Runtime only
- Requires pre-converted models

### 3. Manual Installation

For advanced users who prefer manual control:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install system dependencies
sudo apt update
sudo apt install -y python3-dev build-essential cmake \
    libasound2-dev portaudio19-dev ffmpeg

# 3. Install Python packages (without PyTorch)
pip install numpy scipy transformers onnxruntime
pip install pyaudio fastapi uvicorn

# 4. Install optional tools
pip install openai-whisper  # If PyTorch available
```

---

## NPU Acceleration

### ENNP SDK Setup

To enable NPU acceleration, install the ENNP SDK from ESWIN:

#### 1. Download ENNP SDK

Visit [ESWIN Computing](https://www.eswincomputing.com) and download:
- **ENNP Runtime** (for inference)
- **ENNP Toolkit** (for model conversion)

#### 2. Install ENNP SDK

```bash
# Extract SDK package
tar -xzf ennp-sdk-*.tar.gz
cd ennp-sdk

# Install runtime
sudo ./install.sh

# Verify installation
ls /usr/lib/libennp.so
ls /opt/eswin/ennp
```

#### 3. Install ONNX Runtime with ENNP EP

```bash
# Install ONNX Runtime (if not already installed)
pip install onnxruntime

# Check for ENNP Execution Provider
python3 -c "import onnxruntime; print(onnxruntime.get_available_providers())"
```

Expected output should include:
```
['ENNPExecutionProvider', 'CPUExecutionProvider']
```

### Verify NPU Detection

```bash
# Run hardware detection
python3 -c "
from src.utils.hardware import get_hardware_detector
hw = get_hardware_detector()
info = hw.get_system_info()
print(f'SoC: {info[\"soc_type\"]}')
print(f'NPU: {info[\"npu_info\"][\"description\"]}')
"
```

Expected output:
```
SoC: eic7700
NPU: ESWIN EIC7700 NPU (13.3 TOPS INT8)
```

---

## Model Conversion

### Why Convert Models?

- **NPU Optimization**: Native ENNP format enables NPU acceleration
- **Quantization**: INT8 reduces memory and increases speed
- **Compatibility**: ONNX format works across platforms

### Convert Whisper Model

```bash
# Convert Whisper base model to ONNX
python3 scripts/convert_models_npu.py \
    --model whisper \
    --size base \
    --format onnx

# Convert to ENNP (requires ENNP SDK)
python3 scripts/convert_models_npu.py \
    --model whisper \
    --size base \
    --format ennp
```

### Convert Qwen Model

```bash
# Convert Qwen model to ONNX
python3 scripts/convert_models_npu.py \
    --model qwen \
    --size Qwen/Qwen2.5-3B-Instruct \
    --format onnx

# Note: Large language models work best with ONNX Runtime + ENNP EP
```

### Model Storage Structure

After conversion, models should be organized as:

```
models/
├── onnx/
│   ├── whisper_base.onnx
│   ├── whisper_base_quantized.onnx
│   └── qwen2.5_3b_instruct.onnx
├── eic7700/
│   ├── whisper_base.ennp
│   └── qwen2.5_3b_instruct.onnx
```

---

## Performance Optimization

### 1. Enable NPU Acceleration in Config

Edit `config.yaml`:

```yaml
# Speech-to-Text models
stt:
  default_engine: "whisper"
  engines:
    whisper:
      model_size: "base"
      device: "cpu"  # ONNX Runtime will use ENNP EP
      use_npu: true   # Enable NPU acceleration

# Summarization models
summarization:
  default_engine: "qwen3"
  engines:
    qwen3:
      model_name: "Qwen/Qwen2.5-3B-Instruct"
      device: "cpu"   # ONNX Runtime will use ENNP EP
      use_npu: true   # Enable NPU acceleration
```

### 2. Optimize System Settings

```bash
# Set CPU governor to performance
sudo sh -c 'echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'

# Increase swap if needed (for model loading)
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=4096/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 3. Memory Management

For systems with limited RAM:

```yaml
# Use smaller models
stt:
  engines:
    whisper:
      model_size: "tiny"  # or "base"

summarization:
  engines:
    qwen3:
      model_name: "Qwen/Qwen2.5-1.5B-Instruct"  # Smaller model
```

### 4. Concurrent Processing

Enable efficient resource usage:

```yaml
processing:
  real_time_stt: true
  auto_summarize: false  # Summarize after recording ends
  chunk_duration: 30     # Process in 30-second chunks
```

---

## Benchmarking

### Run Performance Benchmark

```bash
# Full benchmark (Whisper + Qwen)
python3 scripts/benchmark_riscv.py

# Whisper only
python3 scripts/benchmark_riscv.py --whisper-only

# Qwen only
python3 scripts/benchmark_riscv.py --qwen-only

# Custom iterations
python3 scripts/benchmark_riscv.py --iterations 10
```

### Expected Performance

#### EIC7700 (13.3 TOPS)

| Model | Backend | Throughput | Speedup |
|-------|---------|------------|---------|
| Whisper Base | CPU | 0.8x realtime | - |
| Whisper Base | NPU | 2.5x realtime | 3.1x |
| Qwen 3B | CPU | 8 tokens/s | - |
| Qwen 3B | NPU | 25 tokens/s | 3.1x |

#### EIC7700X (19.95 TOPS)

| Model | Backend | Throughput | Speedup |
|-------|---------|------------|---------|
| Whisper Small | CPU | 0.5x realtime | - |
| Whisper Small | NPU | 2.0x realtime | 4.0x |
| Qwen 3B | CPU | 8 tokens/s | - |
| Qwen 3B | NPU | 35 tokens/s | 4.4x |

### Interpret Results

Results are saved to `benchmark_results/benchmark_YYYYMMDD_HHMMSS.json`:

```json
{
  "system": {
    "architecture": "riscv64",
    "soc_type": "eic7700",
    "npu_info": {
      "available": true,
      "type": "eic7700",
      "tops": 13.3,
      "description": "ESWIN EIC7700 NPU (13.3 TOPS INT8)"
    }
  },
  "whisper": {
    "cpu": {
      "avg_time": 37.5,
      "throughput": 0.8
    },
    "npu": {
      "avg_time": 12.0,
      "throughput": 2.5,
      "speedup": 3.1
    }
  }
}
```

---

## Troubleshooting

### NPU Not Detected

**Problem**: `NPU: Not Available` in system info

**Solutions**:

1. Check ENNP SDK installation:
```bash
ls /usr/lib/libennp.so
```

2. Verify device nodes:
```bash
ls /dev/ennp
ls /dev/eswin-npu
```

3. Check kernel module:
```bash
lsmod | grep ennp
```

4. Reinstall ENNP SDK

### ONNX Runtime No ENNP Provider

**Problem**: `ENNPExecutionProvider` not in available providers

**Solutions**:

1. Install ONNX Runtime with ENNP support:
```bash
# Download ENNP-enabled ONNX Runtime from ESWIN
pip install onnxruntime-ennp-*.whl
```

2. Or build from source with ENNP support

### Model Conversion Fails

**Problem**: `esquant` or `esaac` command not found

**Solutions**:

1. Add ENNP toolkit to PATH:
```bash
export PATH=$PATH:/opt/eswin/ennp/bin
```

2. Or install ENNP toolkit:
```bash
# Download from ESWIN website
sudo dpkg -i ennp-toolkit_*.deb
```

### Poor Performance on NPU

**Problem**: NPU performance worse than expected

**Solutions**:

1. Ensure model is quantized (INT8):
```bash
# Reconvert with quantization
python3 scripts/convert_models_npu.py --model whisper --size base --format ennp
```

2. Check NPU utilization:
```bash
# Monitor NPU (if tools available)
ennp-smi
```

3. Verify no CPU fallback:
```python
# Check logs for "Using CPU" warnings
tail -f logs/meeting_assistant.log | grep -i cpu
```

### Out of Memory

**Problem**: System runs out of memory during inference

**Solutions**:

1. Use smaller models:
```yaml
stt:
  engines:
    whisper:
      model_size: "tiny"  # Instead of "base"
```

2. Increase swap:
```bash
sudo swapoff -a
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
sudo mkswap /swapfile
sudo swapon /swapfile
```

3. Close other applications

### Audio Input Not Working

**Problem**: No microphone detected

**Solutions**:

1. List audio devices:
```bash
arecord -l
```

2. Test recording:
```bash
arecord -d 5 test.wav
aplay test.wav
```

3. Check permissions:
```bash
sudo usermod -a -G audio $USER
# Log out and log back in
```

---

## Additional Resources

- **ESWIN Computing**: https://www.eswincomputing.com
- **ENNP SDK Documentation**: Contact ESWIN for access
- **RISC-V International**: https://riscv.org
- **ONNX Runtime**: https://onnxruntime.ai

---

## Performance Tips

1. **Use quantized models** for best NPU performance
2. **Enable ENNP Execution Provider** in ONNX Runtime
3. **Use smaller models** on systems with limited RAM
4. **Process audio in chunks** for real-time performance
5. **Monitor system resources** during operation
6. **Keep ENNP SDK updated** for latest optimizations

---

## Next Steps

1. ✅ Install Meeting Assistant with ONNX Runtime
2. ✅ Install ENNP SDK for NPU acceleration
3. ✅ Convert models to ONNX/ENNP format
4. ✅ Run benchmarks to verify performance
5. ✅ Configure application for your use case
6. ✅ Test with real meetings

For more help, see the main [README.md](../README.md) or open an issue on GitHub.
