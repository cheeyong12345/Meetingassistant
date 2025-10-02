# Meeting Assistant

AI-powered meeting transcription and summarization tool with multi-model support, designed for local deployment on ARM64 SBCs including RK3588.

## Features

### Core Capabilities
- **Real-time Speech-to-Text** with multiple engine support
- **AI-powered Summarization** with changeable local models
- **Meeting Recording** with automatic processing
- **Multi-modal Interface** (CLI and Web)
- **Local Deployment** for privacy and offline operation

### Supported Models

#### Speech-to-Text Engines
- **Whisper** (OpenAI) - High accuracy, 99+ languages
- **Vosk** - Lightweight offline recognition
- **Google Speech-to-Text** (API-based, optional)

#### Summarization Engines
- **Qwen 3** (Alibaba) - Local transformer model
- **Ollama** - Local model server with model switching
- **OpenAI GPT** (API-based, optional)

### Hardware Support
- **ARM64 SBCs**: RK3588, Raspberry Pi 4/5, Orange Pi
- **x86_64**: Desktop and laptop computers
- **NPU Acceleration**: RK3588 Neural Processing Unit support
- **GPU Acceleration**: CUDA, Metal, OpenCL support

## Quick Start

### Installation Options

Choose the installation that best fits your needs:

#### 1. Full Installation (Recommended for SBC/Local)
Complete setup with local models for offline operation:
```bash
python3 scripts/install_sbc.py
```
- **Size**: 2-7GB (depending on model choices)
- **Features**: Offline STT + summarization
- **Best for**: RK3588, Raspberry Pi, offline use

#### 2. Lightweight Installation
Minimal setup using API-based services:
```bash
python3 scripts/install_lightweight.py
```
- **Size**: ~50MB
- **Features**: API-based STT + summarization
- **Best for**: Testing, low-storage systems
- **Requires**: Internet + API keys

#### 3. Manual Installation
Custom setup for developers:
```bash
pip install -r requirements.txt
```

### Interactive Model Selection

The full installer now provides choices for:

**STT Models:**
1. **Whisper** (Recommended) - Sizes: tiny(40MB), base(150MB), small(500MB), medium(1.5GB)
2. **Vosk** - Options: standard(22MB), large(1.8GB), lightweight(50MB)
3. **Both** - Maximum compatibility
4. **Skip** - Manual installation later

**Summarization Models:**
1. **Qwen** - Sizes: 1.8B(2GB), 3B(3.5GB), 7B(7GB)
2. **Ollama** - Easy model switching, various sizes
3. **Both** - Maximum flexibility
4. **Skip** - API-based only

### Post-Installation Testing

```bash
# Quick system check
python3 test.py quick

# Audio devices and engines
python3 test.py setup

# Complete functionality test
python3 test.py complete

# Run all tests
python3 test.py all
```

## Usage

### CLI Interface

**Start a meeting:**
```bash
python cli.py record --title "Team Standup" --participants "John,Sarah,Mike"
```

**Transcribe audio file:**
```bash
python cli.py transcribe audio_file.wav
```

**Summarize text:**
```bash
python cli.py summarize transcript.txt
```

**List available engines:**
```bash
python cli.py engines
```

**Switch engines:**
```bash
python cli.py engines --stt-engine whisper --sum-engine qwen3
```

**Test system:**
```bash
python cli.py test
```

### Web Interface

**Start web server:**
```bash
python3 web_app.py
# Or use the launcher script:
python3 run_web.py
```

**Access interface:**
- Open browser to `http://localhost:8000`
- Dashboard: Real-time meeting control
- Transcribe: Upload and process audio files
- Settings: Configure engines and preferences

## Configuration

Edit `config.yaml` to customize settings:

```yaml
# Audio settings
audio:
  sample_rate: 16000
  input_device: null  # Auto-detect

# STT engines
stt:
  default_engine: "whisper"
  engines:
    whisper:
      model_size: "base"  # tiny, base, small, medium, large
      language: "auto"

# Summarization engines
summarization:
  default_engine: "qwen3"
  engines:
    qwen3:
      model_name: "Qwen/Qwen2.5-3B-Instruct"
      max_tokens: 1000

# Processing settings
processing:
  real_time_stt: true
  auto_summarize: true
  chunk_duration: 30
```

## Hardware Optimization

### RK3588 NPU Support

The RK3588's 6 TOPS NPU provides excellent performance:

- **Real-time STT**: Whisper-small at 2x real-time speed
- **AI Summarization**: Qwen 3-3B with <500ms latency
- **Concurrent Processing**: STT + summarization simultaneously
- **Power Efficiency**: 8-12W total system power

### Performance Expectations

| Hardware | STT Performance | Summarization | Concurrent |
|----------|----------------|---------------|------------|
| RK3588 NPU | 2x real-time | 10-15 tok/sec | ✅ |
| RPi 4 (4GB) | 0.5x real-time | 2-3 tok/sec | ❌ |
| x86 CPU | 1-3x real-time | 5-10 tok/sec | ✅ |
| x86 + GPU | 5-10x real-time | 20-50 tok/sec | ✅ |

## File Structure

```
Meetingassistant/
├── README.md             # This file
├── config.yaml           # Configuration file
├── requirements.txt      # Python dependencies
│
├── src/                  # Source code
│   ├── config.py         # Configuration management
│   ├── meeting.py        # Main meeting assistant
│   ├── audio/            # Audio recording
│   ├── stt/              # Speech-to-text engines
│   └── summarization/    # Summarization engines
│
├── scripts/              # Utility scripts
│   ├── install_sbc.py           # Full installation
│   ├── install_lightweight.py   # Lightweight installation
│   └── start_demo.sh            # Quick start script
│
├── docs/                 # Documentation
│   ├── guides/           # User guides
│   ├── reviews/          # Technical reviews
│   └── design/           # Design documentation
│
├── templates/            # Web templates
├── static/               # Web assets (CSS, JS)
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript
│
├── tests/                # Test files
├── data/                 # Meeting recordings
└── models/               # AI models
```

## Development

### Adding New STT Engines

1. Create new engine in `src/stt/`
2. Inherit from `STTEngine` base class
3. Register in `STTManager`
4. Update configuration

### Adding New Summarization Engines

1. Create new engine in `src/summarization/`
2. Inherit from `SummarizationEngine` base class
3. Register in `SummarizationManager`
4. Update configuration

### Custom NPU Integration

For custom NPU support:

1. Implement model conversion pipeline
2. Add NPU runtime detection
3. Create optimized inference engine
4. Update hardware detection logic

## Troubleshooting

### Audio Issues

**No microphone detected:**
```bash
# Check audio devices
arecord -l
# Test microphone
arecord -d 5 test.wav && aplay test.wav
```

**Permission errors:**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Restart session
```

### Model Loading Issues

**Insufficient memory:**
- Use smaller models (e.g., whisper-tiny, qwen-1.8b)
- Increase swap space
- Close other applications

**Download failures:**
- Check internet connection
- Use manual model download
- Check storage space

### Performance Issues

**Slow transcription:**
- Use smaller Whisper model
- Enable NPU/GPU acceleration
- Check CPU/memory usage

**High latency:**
- Reduce chunk duration
- Use faster models
- Enable real-time processing

## License

[License information]

## Contributing

[Contribution guidelines]

## Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting section
- Review configuration guide