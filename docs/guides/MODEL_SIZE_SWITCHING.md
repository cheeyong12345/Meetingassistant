# Whisper Model Size Switching

Dynamic model size switching for Whisper.cpp STT engine via web interface.

## Overview

You can now change the Whisper.cpp model size directly from the web interface without editing config files or restarting the application.

## Features

✅ **Dynamic Switching** - Change models in real-time via Settings page
✅ **Auto-Detection** - Automatically shows available downloaded models
✅ **Smart UI** - Model selector only appears for whisper.cpp engine
✅ **Validation** - Checks if model exists before switching
✅ **Helpful Errors** - Provides download instructions if model missing

## How to Use

### 1. Access Settings Page

```
http://localhost:8000/settings
```

### 2. Check Current STT Engine

Make sure you're using **whispercpp** engine. The model size selector will appear automatically.

### 3. Select Model Size

You'll see a dropdown with all available models:
- `tiny` - 75MB, fastest, lowest accuracy
- `base` - 150MB, balanced (default)
- `small` - 500MB, better accuracy
- `medium` - 1.5GB, high accuracy
- `large` - 3GB, highest accuracy

### 4. Click "Change Model"

The model will switch immediately. Page will reload to confirm the change.

## Downloading Models

If you want to use a model that's not in the list, download it first:

```bash
cd ~/whisper.cpp
bash ./models/download-ggml-model.sh medium  # or small, large, etc.
```

Then refresh the Settings page - the new model will appear in the dropdown.

## API Endpoints

For programmatic access:

### Get Available Models
```bash
curl http://localhost:8000/api/engines/stt/models
```

Response:
```json
{
  "success": true,
  "models": ["base", "medium", "small"],
  "current": "base"
}
```

### Change Model
```bash
curl -X POST http://localhost:8000/api/engines/stt/model \
  -d "model_size=medium"
```

Response:
```json
{
  "success": true,
  "model_size": "medium",
  "message": "Successfully changed to medium model"
}
```

## Technical Details

### Files Modified
- `src/stt/whispercpp_engine.py` - Added `set_model_size()` and `get_available_models()`
- `web_app.py` - Added API endpoints `/api/engines/stt/model` and `/api/engines/stt/models`
- `templates/settings.html` - Added model size selector UI and JavaScript

### How It Works

1. **Detection**: JavaScript checks if current STT engine is whispercpp
2. **Load Models**: Fetches available models via `/api/engines/stt/models`
3. **Display**: Shows dropdown with all downloaded models
4. **Switch**: POST to `/api/engines/stt/model` with new model_size
5. **Validation**: Backend checks if model file exists
6. **Update**: Model path updated, engine keeps running

### Benefits Over Config Method

**Old Way (config.yaml):**
```yaml
stt:
  engines:
    whispercpp:
      model_size: base  # Edit this
```
❌ Requires config file editing
❌ Need to restart app
❌ Easy to make syntax errors

**New Way (Web UI):**
✅ Click dropdown, select model
✅ No restart needed
✅ Instant validation
✅ User-friendly

## Error Handling

### Model Not Found
```
Failed to change model to medium. Model may not be downloaded.
```

**Solution**: Download the model:
```bash
cd ~/whisper.cpp && bash ./models/download-ggml-model.sh medium
```

### Engine Not Supporting Switching
```
Current STT engine does not support model switching
```

**Solution**: This feature only works with `whispercpp` engine. Switch to whispercpp first.

## RISC-V Notes

On RISC-V systems:
- Model switching works exactly the same way
- All models stored in `~/whisper.cpp/models/`
- No PyTorch needed - pure C++ implementation
- Model files: `ggml-{size}.bin`

## Limitations

- ⚠️ Can only switch between **already downloaded** models
- ⚠️ Feature specific to **whisper.cpp engine** only
- ⚠️ During model switch, brief interruption if transcribing

## Future Enhancements

Potential improvements:
- Download models directly from web UI
- Show model size and memory requirements
- Automatic model recommendation based on system specs
- Model performance metrics

---

**Last Updated**: 2025-10-03
**Feature Version**: 1.0
**Supported Engines**: whisper.cpp
