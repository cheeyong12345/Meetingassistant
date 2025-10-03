# Normal Mode vs Debug Mode - Comparison

## Quick Comparison

| Feature | Normal Mode | Debug Mode |
|---------|-------------|------------|
| **Port** | 8000 | 8001 |
| **Log Level** | INFO | DEBUG |
| **Console Output** | Minimal | Verbose |
| **Log Files** | None | Multiple (debug.log, error.log) |
| **Audio Saved** | No | Yes (debug/audio/) |
| **Results Saved** | Database only | Database + JSON files |
| **Stack Traces** | Errors only | All exceptions |
| **Performance Metrics** | No | Yes |
| **Config File** | config.yaml | debug/config_debug.yaml |

---

## Output Examples

### Example 1: Starting Application

**Normal Mode:**
```
INFO: Starting Meeting Assistant
INFO: Loading Whisper model
INFO: Model loaded successfully
INFO: Server started on port 8000
```

**Debug Mode:**
```
[2025-10-03 10:23:45] INFO     [run_debug:main:67] Starting Meeting Assistant in DEBUG mode
[2025-10-03 10:23:45] DEBUG    [run_debug:main:68] Working directory: /home/amd/Meetingassistant
[2025-10-03 10:23:45] DEBUG    [run_debug:main:69] Config file: debug/config_debug.yaml
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:45] ================================================================
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:46] SYSTEM INFORMATION
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:47] ================================================================
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:51] Python version: 3.12.6
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:52] Platform: Linux-6.14.0-33-generic-riscv64-with-glibc2.38
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:53] Architecture: riscv64
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:61] SoC Type: eic7700
[2025-10-03 10:23:45] INFO     [run_debug:print_system_info:65] NPU: ESWIN EIC7700 NPU (13.3 TOPS INT8)
[2025-10-03 10:23:45] DEBUG    [whisper_engine:__init__:18] Initializing Whisper engine
[2025-10-03 10:23:45] DEBUG    [whisper_engine:initialize:33] Auto-detecting device
[2025-10-03 10:23:45] INFO     [whisper_engine:initialize:38] NPU detected: ESWIN EIC7700 NPU (13.3 TOPS INT8)
[2025-10-03 10:23:46] DEBUG    [whisper_engine:initialize:42] Checking for NPU model at ./models/eic7700/whisper_base
[2025-10-03 10:23:46] INFO     [whisper_engine:initialize:52] Whisper model loaded on NPU successfully
[2025-10-03 10:23:46] INFO     [run_debug:main:89] Starting FastAPI server in debug mode...
[2025-10-03 10:23:46] INFO     [run_debug:main:90] Access the application at: http://localhost:8001
```

---

### Example 2: Transcribing Audio

**Normal Mode:**
```
INFO: Transcribing audio
INFO: Transcription complete
```

**Debug Mode:**
```
[2025-10-03 10:25:10] INFO     [whisper_engine:transcribe:86] Starting transcription
[2025-10-03 10:25:10] DEBUG    [whisper_engine:transcribe:91] Audio data type: <class 'numpy.ndarray'>
[2025-10-03 10:25:10] DEBUG    [whisper_engine:transcribe:92] Audio data shape: (480000,)
[2025-10-03 10:25:10] DEBUG    [whisper_engine:transcribe:93] Audio duration: 30.0 seconds
[2025-10-03 10:25:10] DEBUG    [whisper_engine:transcribe:94] Using NPU accelerator: True
[2025-10-03 10:25:11] DEBUG    [npu_acceleration:infer:242] Running inference on ENNP
[2025-10-03 10:25:11] DEBUG    [npu_acceleration:infer:243] Input shape: (1, 80, 3000)
[2025-10-03 10:25:13] DEBUG    [npu_acceleration:infer:250] Inference completed in 2.15s
[2025-10-03 10:25:13] DEBUG    [whisper_engine:transcribe:102] Post-processing results
[2025-10-03 10:25:13] DEBUG    [whisper_engine:transcribe:105] Found 12 segments
[2025-10-03 10:25:13] INFO     [whisper_engine:transcribe:108] Transcription completed in 3.21s
[2025-10-03 10:25:13] DEBUG    [whisper_engine:transcribe:109] Saving results to debug/stt_results/
```

---

### Example 3: Error Handling

**Normal Mode:**
```
ERROR: Failed to load model
```

**Debug Mode:**
```
[2025-10-03 10:30:15] ERROR    [whisper_engine:initialize:65] Failed to load model
[2025-10-03 10:30:15] DEBUG    [whisper_engine:initialize:66] Exception details:
Traceback (most recent call last):
  File "/home/amd/Meetingassistant/src/stt/whisper_engine.py", line 63, in initialize
    self.model = whisper.load_model(self.model_size, device=self.device)
  File "/venv/lib/python3.12/site-packages/whisper/__init__.py", line 124, in load_model
    checkpoint_file = _download(_MODELS[name])
  File "/venv/lib/python3.12/site-packages/whisper/__init__.py", line 37, in _download
    raise RuntimeError(f"Model {name} not found")
RuntimeError: Model base not found; available models = ['tiny.en', 'tiny', 'small']
[2025-10-03 10:30:15] INFO     [whisper_engine:initialize:68] Attempting fallback to CPU
[2025-10-03 10:30:15] DEBUG    [whisper_engine:initialize:69] Downloading model from repository
```

---

### Example 4: NPU Detection

**Normal Mode:**
```
INFO: NPU detected: ESWIN EIC7700 NPU (13.3 TOPS INT8)
```

**Debug Mode:**
```
[2025-10-03 10:35:20] DEBUG    [hardware:_detect_hardware:29] Starting hardware detection
[2025-10-03 10:35:20] DEBUG    [hardware:_detect_soc_type:38] Reading device tree model
[2025-10-03 10:35:20] DEBUG    [hardware:_detect_soc_type:42] Device tree content: ESWIN EIC7700 StarPro64 Kernel
[2025-10-03 10:35:20] INFO     [hardware:_detect_soc_type:54] Detected EIC7700 RISC-V SoC: ESWIN EIC7700 StarPro64 Kernel
[2025-10-03 10:35:20] DEBUG    [hardware:_detect_npu:112] Detecting NPU hardware
[2025-10-03 10:35:20] DEBUG    [hardware:_detect_eic7700_npu:156] Checking for ENNP device nodes
[2025-10-03 10:35:20] DEBUG    [hardware:_detect_eic7700_npu:162] Found ENNP device node: /dev/ennp
[2025-10-03 10:35:20] INFO     [hardware:_detect_eic7700_npu:167] EIC7700 NPU detected at /dev/ennp
[2025-10-03 10:35:20] DEBUG    [hardware:_get_eic7700_tops:196] Checking for EIC7700X variant
[2025-10-03 10:35:20] INFO     [hardware:_get_eic7700_tops:207] Detected EIC7700 standard variant (13.3 TOPS)
[2025-10-03 10:35:20] INFO     [hardware:get_npu_info:258] NPU available: eic7700 (13.3 TOPS)
```

---

## File Structure

### Normal Mode Files

```
Meetingassistant/
├── config.yaml          # Production config
├── web_app.py          # Web server
├── cli.py              # CLI
├── data/               # Meeting data
│   └── meetings.db     # Database
└── src/                # Source code
```

### Debug Mode Files

```
Meetingassistant/
├── debug/
│   ├── config_debug.yaml         # Debug config
│   ├── run_debug.py              # Debug web server
│   ├── run_debug_cli.py          # Debug CLI
│   ├── test_debug_logging.py    # Test logging
│   ├── README_DEBUG.md           # Documentation
│   ├── logs/                     # All logs
│   │   ├── debug_20251003_102345.log
│   │   ├── error_20251003_102345.log
│   │   ├── cli_debug_*.log
│   │   └── cli_error_*.log
│   ├── audio/                    # Saved audio files
│   ├── audio_chunks/             # Audio chunks
│   ├── stt_results/              # Transcription JSONs
│   ├── summaries/                # Summary JSONs
│   ├── profiles/                 # Performance profiles
│   └── data/                     # Debug database
│       └── meetings.db
```

---

## When to Use Each Mode

### Use Normal Mode When:

- ✅ Running in production
- ✅ Performance is critical
- ✅ Disk space is limited
- ✅ Everything is working correctly
- ✅ You only need final results

### Use Debug Mode When:

- 🔍 Troubleshooting issues
- 🔍 Developing new features
- 🔍 Testing NPU integration
- 🔍 Analyzing performance
- 🔍 Learning how the system works
- 🔍 Reporting bugs
- 🔍 Optimizing for RISC-V

---

## Performance Impact

### Normal Mode

- **CPU Usage**: 20-40% (during processing)
- **Memory**: 2-4GB (with base models)
- **Disk I/O**: Minimal
- **Log Size**: None

### Debug Mode

- **CPU Usage**: 25-45% (5-10% overhead for logging)
- **Memory**: 2.5-4.5GB (extra 500MB for debug data)
- **Disk I/O**: High (continuous log writing)
- **Log Size**: 1-5 MB/hour (depending on activity)

**Recommendation**: Debug mode overhead is acceptable for development and troubleshooting, but use normal mode for production deployments.

---

## Log Retention

### Normal Mode

- No logs created (unless configured separately)
- Database only persistence

### Debug Mode

- Logs accumulate in `debug/logs/`
- **Cleanup recommended every 7-30 days**

```bash
# Remove logs older than 7 days
find debug/logs -name "*.log" -mtime +7 -delete

# Or keep only last 10 log files
cd debug/logs && ls -t *.log | tail -n +11 | xargs rm -f
```

---

## Summary

**Normal Mode** = Production-ready, minimal output, performance-focused
**Debug Mode** = Development-friendly, verbose output, diagnostic-focused

Both modes can run simultaneously on different ports (8000 vs 8001)!
