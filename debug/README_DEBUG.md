# Debug Mode - Meeting Assistant

This folder contains debug versions of the Meeting Assistant with comprehensive logging enabled.

## 📁 Contents

```
debug/
├── config_debug.yaml       # Debug configuration (all logging enabled)
├── run_debug.py           # Web app launcher with debug mode
├── run_debug_cli.py       # CLI launcher with debug mode
├── README_DEBUG.md        # This file
├── logs/                  # Debug and error logs (auto-created)
├── audio/                 # Saved audio files (auto-created)
├── audio_chunks/          # Saved audio chunks (auto-created)
├── stt_results/           # Transcription results (auto-created)
├── summaries/             # Summarization results (auto-created)
├── profiles/              # Performance profiles (auto-created)
└── data/                  # Debug database and meeting data (auto-created)
```

## 🚀 Quick Start

### Web Interface (Debug Mode)

```bash
# Run web app with full debug logging
python3 debug/run_debug.py
```

Access at: **http://localhost:8001** (note: different port from production)

### CLI (Debug Mode)

```bash
# Run CLI with debug logging
python3 debug/run_debug_cli.py <command> [options]

# Examples:
python3 debug/run_debug_cli.py test
python3 debug/run_debug_cli.py devices
python3 debug/run_debug_cli.py record --duration 60
```

## 📊 What's Different in Debug Mode?

### 1. Verbose Logging

**Normal mode:**
```
INFO: Whisper model loaded
INFO: Transcription complete
```

**Debug mode:**
```
[2025-01-03 10:23:45] DEBUG    [whisper_engine:initialize:28] Detected RISC-V architecture
[2025-01-03 10:23:45] DEBUG    [whisper_engine:initialize:33] Auto-detecting device
[2025-01-03 10:23:45] INFO     [whisper_engine:initialize:38] NPU detected: ESWIN EIC7700 NPU (13.3 TOPS INT8)
[2025-01-03 10:23:45] DEBUG    [whisper_engine:initialize:42] Checking for NPU model at ./models/eic7700/whisper_base
[2025-01-03 10:23:46] INFO     [whisper_engine:initialize:52] Whisper model loaded on NPU successfully
[2025-01-03 10:23:46] DEBUG    [whisper_engine:transcribe:87] Starting transcription
[2025-01-03 10:23:46] DEBUG    [whisper_engine:transcribe:91] Audio data shape: (480000,)
[2025-01-03 10:23:50] DEBUG    [whisper_engine:transcribe:95] Transcription took 3.82s
[2025-01-03 10:23:50] INFO     [whisper_engine:transcribe:97] Transcription complete
```

### 2. All Logging Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages
- **CRITICAL**: Critical errors that may crash the app

### 3. Multiple Log Files

**Created automatically:**
- `debug/logs/debug_YYYYMMDD_HHMMSS.log` - All logs (DEBUG and above)
- `debug/logs/error_YYYYMMDD_HHMMSS.log` - Errors only
- `debug/logs/cli_debug_*.log` - CLI debug logs
- `debug/logs/cli_error_*.log` - CLI error logs

### 4. Saved Debug Data

**Audio files:**
- `debug/audio/` - Full audio recordings
- `debug/audio_chunks/` - Individual audio chunks

**Results:**
- `debug/stt_results/` - Transcription JSON results
- `debug/summaries/` - Summary JSON results

**Performance:**
- `debug/profiles/` - Performance profiling data

### 5. Enhanced Error Information

**Normal mode:**
```
ERROR: Failed to load model
```

**Debug mode:**
```
[2025-01-03 10:25:30] ERROR    [whisper_engine:initialize:65] Failed to load model
[2025-01-03 10:25:30] DEBUG    [whisper_engine:initialize:66] Exception details:
Traceback (most recent call last):
  File "/home/amd/Meetingassistant/src/stt/whisper_engine.py", line 63, in initialize
    self.model = whisper.load_model(self.model_size, device=self.device)
  File "/home/amd/Meetingassistant/venv/lib/python3.12/site-packages/whisper/__init__.py", line 124, in load_model
    raise RuntimeError(f"Model {name} not found")
RuntimeError: Model base not found
[2025-01-03 10:25:30] INFO     [whisper_engine:initialize:68] Falling back to CPU
```

## 🔍 Reading Debug Logs

### Real-time Log Monitoring

```bash
# Watch debug log in real-time
tail -f debug/logs/debug_*.log

# Watch error log in real-time
tail -f debug/logs/error_*.log

# Filter for specific component
tail -f debug/logs/debug_*.log | grep whisper_engine

# Filter for errors only
tail -f debug/logs/debug_*.log | grep ERROR
```

### Searching Logs

```bash
# Find all NPU-related logs
grep -r "NPU" debug/logs/

# Find all errors
grep -r "ERROR" debug/logs/

# Find specific function calls
grep -r "transcribe:" debug/logs/

# Find performance metrics
grep -r "took.*s$" debug/logs/
```

## 📈 Performance Profiling

Debug mode includes execution time logging:

```
[2025-01-03 10:30:15] DEBUG    [whisper_engine:transcribe:95] Transcription took 3.82s
[2025-01-03 10:30:20] DEBUG    [qwen_engine:summarize:138] Summarization took 5.21s
[2025-01-03 10:30:21] DEBUG    [meeting:process:245] Total processing took 9.15s
```

## 🐛 Debugging Common Issues

### Issue: NPU Not Being Used

**Check debug logs:**
```bash
grep -i "npu" debug/logs/debug_*.log
```

**Look for:**
- `NPU detected: ...`
- `Loading NPU-optimized model`
- `NPU model loaded successfully`

**If you see:**
- `NPU model not found` → Convert models first
- `Failed to load NPU model` → Check ENNP SDK installation
- `Falling back to CPU` → NPU initialization failed

### Issue: Poor Performance

**Check execution times:**
```bash
grep "took.*s$" debug/logs/debug_*.log | tail -20
```

**Compare:**
- CPU vs NPU times
- Expected vs actual throughput

### Issue: Crashes or Errors

**Check error log:**
```bash
cat debug/logs/error_*.log
```

**Look for:**
- Stack traces showing where error occurred
- Error messages with details
- Memory issues (OOM errors)

### Issue: Import Errors

**Check dependency section in log:**
```bash
grep "DEPENDENCY CHECK" -A 20 debug/logs/debug_*.log
```

**Look for:**
- ❌ marks indicating missing packages
- Version mismatches

## 🔧 Configuration

Edit `debug/config_debug.yaml` to customize:

```yaml
# Change log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
app:
  log_level: "DEBUG"

# Save audio files for debugging
audio:
  debug_save_audio: true
  debug_audio_dir: "debug/audio"

# Save transcription results
stt:
  debug_mode: true
  engines:
    whisper:
      debug_save_results: true
```

## 📊 Log Format

```
[TIMESTAMP] LEVEL [MODULE:FUNCTION:LINE] MESSAGE
```

**Example:**
```
[2025-01-03 10:23:45] INFO [whisper_engine:initialize:52] Model loaded successfully
│                      │     │              │         │    │
│                      │     │              │         │    └─ Message
│                      │     │              │         └────── Line number
│                      │     │              └──────────────── Function name
│                      │     └─────────────────────────────── Module name
│                      └───────────────────────────────────── Log level
└──────────────────────────────────────────────────────────── Timestamp
```

## 🧹 Cleanup

Debug mode can generate large log files. Clean up periodically:

```bash
# Remove old logs (older than 7 days)
find debug/logs -name "*.log" -mtime +7 -delete

# Remove all debug data
rm -rf debug/logs/* debug/audio/* debug/audio_chunks/* debug/stt_results/* debug/summaries/*

# Keep structure, remove files only
find debug -type f -not -name "*.py" -not -name "*.yaml" -not -name "*.md" -delete
```

## 🔄 Switching Between Modes

**Production mode:**
```bash
python3 web_app.py          # Port 8000, minimal logging
python3 cli.py <command>    # Standard logging
```

**Debug mode:**
```bash
python3 debug/run_debug.py      # Port 8001, full logging
python3 debug/run_debug_cli.py  # Debug logging
```

Both can run simultaneously on different ports!

## 💡 Tips

1. **Always use debug mode when troubleshooting**
2. **Check error log first** for quick issue identification
3. **Use grep to filter** large log files
4. **Save logs** when reporting issues
5. **Compare logs** between working and non-working runs
6. **Monitor in real-time** with `tail -f`
7. **Clean up old logs** to save disk space

## 📧 Reporting Issues

When reporting bugs, include:

1. **Error log**: `debug/logs/error_*.log`
2. **Debug log excerpt**: Relevant sections from `debug/logs/debug_*.log`
3. **System info**: First 50 lines of debug log (contains system info)
4. **Configuration**: Your `debug/config_debug.yaml`
5. **Steps to reproduce**: What you did before the error

## 🆘 Need Help?

1. Check the main [README.md](../README.md)
2. Review [RISC-V Deployment Guide](../docs/RISCV_DEPLOYMENT.md)
3. Search debug logs for error messages
4. Open an issue with debug logs attached

---

**Remember**: Debug mode generates **verbose output**. Use it for development and troubleshooting, not for production deployments.
