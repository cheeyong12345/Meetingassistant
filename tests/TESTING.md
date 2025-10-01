# Meeting Assistant Testing Guide

This document explains how to test all components of the Meeting Assistant to verify functionality.

## Test Scripts Overview

### 1. `quick_test.py` - Component Verification
**Purpose**: Fast check of all dependencies and components without heavy model loading
**When to use**: Before installation, after installation, for quick health checks
**Runtime**: ~1 second

```bash
python3 quick_test.py
```

**What it tests**:
- ✅ Core Python imports (yaml, json, etc.)
- ✅ Web framework (FastAPI, Uvicorn)
- ✅ CLI framework (Click, Rich)
- ✅ Audio framework (PyAudio, Pydub)
- ✅ STT engines (Whisper, Vosk)
- ✅ AI engines (PyTorch, Transformers)
- ✅ Configuration loading
- ✅ Module structure
- ✅ File structure
- ✅ Script permissions
- ✅ Audio device detection

### 2. `test_basic.py` - Structure Verification
**Purpose**: Test project structure and basic functionality without dependencies
**When to use**: Before any installation to verify project integrity
**Runtime**: ~1 second

```bash
python3 test_basic.py
```

**What it tests**:
- ✅ All required files present
- ✅ Configuration loading
- ✅ Module imports (basic)
- ✅ Script executability
- ✅ Test data availability

### 3. `test_features.py` - Functionality Testing
**Purpose**: Test actual STT and AI functionality after installation
**When to use**: After successful installation to verify everything works
**Runtime**: 30-120 seconds (depending on models)

```bash
python3 test_features.py
```

**What it tests**:
- ✅ Meeting Assistant initialization
- ✅ Audio transcription with test file
- ✅ Text summarization with test document
- ✅ Engine switching (STT and AI)
- ✅ Audio device detection
- ✅ Web application import
- ✅ CLI application import

### 4. `run_test.py` - Complete Integration Test
**Purpose**: Comprehensive test of all functionality with model loading
**When to use**: After installation for thorough verification
**Runtime**: 60-300 seconds (loads models)

```bash
python3 run_test.py
```

**What it tests**:
- ✅ All imports and dependencies
- ✅ Basic functionality without models
- ✅ Transcription with actual model loading
- ✅ Summarization with actual model loading
- ✅ Web and CLI application readiness

## Testing Workflow

### Before Installation
```bash
# 1. Check project structure
python3 test_basic.py

# 2. Check what components are available
python3 quick_test.py
```

### After Installation
```bash
# 1. Quick component check
python3 quick_test.py

# 2. Test actual functionality
python3 test_features.py

# 3. (Optional) Full integration test
python3 run_test.py
```

### During Development
```bash
# Quick health check
python3 quick_test.py

# Test specific functionality
python3 test_features.py
```

## Understanding Test Results

### Quick Test Results
- **90-100%**: All components ready, full functionality available
- **75-89%**: Most components ready, minor features may be missing
- **50-74%**: Basic functionality available, install missing components
- **<50%**: Major components missing, run installation

### Feature Test Results
- **85-100%**: Fully functional, ready for production use
- **70-84%**: Most features work, some optional features may fail
- **50-69%**: Core features work, some models may need installation
- **<50%**: Major issues, check installation and dependencies

## Common Issues and Solutions

### Dependencies Missing
```bash
# Run installation
./install_sbc.sh          # Full installation
./install_lightweight.sh  # Minimal installation
```

### Models Not Loading
- Check internet connection during installation
- Verify sufficient disk space (2-7GB for models)
- Try smaller models in configuration

### Audio Issues
```bash
# Check audio devices
python3 -c "
import pyaudio
pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    info = pa.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'{i}: {info[\"name\"]}')
"
```

### Permission Issues
```bash
# Fix script permissions
chmod +x *.sh *.py

# Add user to audio group (Linux)
sudo usermod -a -G audio $USER
# (logout and login again)
```

## Test Data Files

### Audio Test File
- **File**: `test_data/test_speech.wav`
- **Content**: Female speaker reading Harvard sentences
- **Duration**: ~33 seconds
- **Format**: 16-bit PCM WAV, 8kHz
- **Use**: Testing STT engines

### Text Test File
- **File**: `test_data/sample_meeting_transcript.txt`
- **Content**: Engineering standup meeting transcript
- **Length**: ~2300 characters
- **Use**: Testing summarization engines

## Manual Testing

### Web Interface
```bash
./run_web.sh
# Open browser to http://localhost:8000
# Test: upload audio, configure engines, start meeting
```

### CLI Interface
```bash
./run_cli.sh devices                          # List audio devices
./run_cli.sh engines                          # List engines
./run_cli.sh transcribe test_data/test_speech.wav
./run_cli.sh summarize test_data/sample_meeting_transcript.txt
./run_cli.sh record --title "Test Meeting"    # Test recording
```

## Performance Expectations

### Hardware Performance
| Hardware | STT Speed | AI Speed | Concurrent |
|----------|-----------|----------|------------|
| RK3588 NPU | 2x real-time | 10-15 tok/sec | ✅ |
| RPi 4 (4GB) | 0.5x real-time | 2-3 tok/sec | ❌ |
| x86 CPU | 1-3x real-time | 5-10 tok/sec | ✅ |
| x86 + GPU | 5-10x real-time | 20-50 tok/sec | ✅ |

### Model Performance
- **Whisper tiny**: ~40MB, fastest, lower accuracy
- **Whisper base**: ~150MB, balanced, good accuracy
- **Whisper small**: ~500MB, better accuracy
- **Qwen 1.8B**: ~2GB, fast summarization
- **Qwen 3B**: ~3.5GB, balanced performance
- **Qwen 7B**: ~7GB, high quality

## Automated Testing

### CI/CD Integration
```bash
# Basic structure test (no dependencies)
python3 test_basic.py

# Component availability test
python3 quick_test.py

# Skip heavy functionality tests in CI
# (models too large for CI environments)
```

### Regression Testing
```bash
# Run before releases
python3 quick_test.py && python3 test_features.py
```

This testing framework ensures reliable functionality across different hardware configurations and installation scenarios.