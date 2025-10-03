#!/usr/bin/env python3
"""
Meeting Assistant Web Interface
Local web interface for the meeting assistant
"""

import sys
import os
from pathlib import Path

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, UploadFile, File
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    import json
    import asyncio
    import time
    import aiofiles
    from typing import List, Dict, Any

    from src.meeting import MeetingAssistant
    from src.config import config

    DEPENDENCIES_AVAILABLE = True

except ImportError as e:
    print(f"❌ Missing web dependencies: {e}")
    print("💡 Run installation script:")
    print("   python3 install_sbc.py         # Full installation")
    print("   python3 install_lightweight.py # Minimal installation")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(title="Meeting Assistant", version="1.0.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global meeting assistant instance
meeting_assistant = None
connected_clients: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize meeting assistant on startup"""
    global meeting_assistant
    meeting_assistant = MeetingAssistant()
    success = meeting_assistant.initialize()
    print(f"Meeting Assistant initialized: {success}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global meeting_assistant
    if meeting_assistant:
        meeting_assistant.cleanup()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard"""
    status = meeting_assistant.get_engine_status() if meeting_assistant else {}
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "status": status
    })

@app.get("/api/status")
async def get_status():
    """Get system status"""
    if not meeting_assistant:
        return {"error": "Meeting assistant not initialized"}

    status = meeting_assistant.get_engine_status()
    meeting_status = meeting_assistant.get_current_meeting_status()

    return {
        "engines": status,
        "meeting": meeting_status,
        "available_engines": {
            "stt": meeting_assistant.get_available_stt_engines(),
            "summarization": meeting_assistant.get_available_summarization_engines()
        }
    }

@app.get("/api/audio-devices")
async def get_audio_devices():
    """Get available audio input devices"""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        devices = []
        current_device = None

        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate'])
                })

        # Get current device from config
        if meeting_assistant and hasattr(meeting_assistant, 'audio_recorder'):
            device_index = meeting_assistant.audio_recorder.device_index
            if device_index is not None:
                device_info = p.get_device_info_by_index(device_index)
                current_device = device_info['name']

        p.terminate()

        return {
            "success": True,
            "devices": devices,
            "current_device": current_device
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "devices": []
        }

@app.post("/api/set-audio-device")
async def set_audio_device(request: Request):
    """Set audio input device"""
    try:
        data = await request.json()
        device_index = data.get('device_index')

        if meeting_assistant and hasattr(meeting_assistant, 'audio_recorder'):
            meeting_assistant.audio_recorder.device_index = device_index
            return {"success": True, "device_index": device_index}
        else:
            return {"success": False, "error": "Audio recorder not available"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/engines/stt")
async def switch_stt_engine(engine: str = Form(...)):
    """Switch STT engine"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    success = meeting_assistant.switch_stt_engine(engine)
    return {"success": success, "engine": engine}

@app.post("/api/engines/summarization")
async def switch_summarization_engine(engine: str = Form(...)):
    """Switch summarization engine"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    success = meeting_assistant.switch_summarization_engine(engine)
    return {"success": success, "engine": engine}

@app.post("/api/engines/stt/model")
async def change_stt_model(model_size: str = Form(...)):
    """Change STT model size (for whisper.cpp)"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    try:
        # Get current STT engine
        stt_manager = meeting_assistant.stt_manager
        current_engine = stt_manager.current_engine

        # Check if current engine supports model changing (whisper.cpp)
        if not hasattr(current_engine, 'set_model_size'):
            return {
                "success": False,
                "error": "Current STT engine does not support model switching"
            }

        # Change model size
        success = current_engine.set_model_size(model_size)

        if success:
            # Update config to persist the change
            config = meeting_assistant.config
            if 'stt' in config and 'engines' in config['stt']:
                engine_name = stt_manager.current_engine_name
                # Find the base engine config (without model suffix)
                for key in config['stt']['engines']:
                    if engine_name.startswith(key):
                        config['stt']['engines'][key]['model_size'] = model_size
                        break

            return {
                "success": True,
                "model_size": model_size,
                "message": f"Successfully changed to {model_size} model"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to change model to {model_size}. Model may not be downloaded."
            }

    except Exception as e:
        logger.error(f"Error changing STT model: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/engines/stt/models")
async def get_available_stt_models():
    """Get available STT models (for whisper.cpp)"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    try:
        stt_manager = meeting_assistant.stt_manager
        current_engine = stt_manager.current_engine

        if hasattr(current_engine, 'get_available_models'):
            available = current_engine.get_available_models()
            current = getattr(current_engine, 'model_size', None)
            return {
                "success": True,
                "models": available,
                "current": current
            }
        else:
            return {
                "success": False,
                "error": "Current engine does not support model listing"
            }
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/meeting/start")
async def start_meeting(title: str = Form(None), participants: str = Form(None)):
    """Start a new meeting"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    # Parse participants
    participant_list = []
    if participants:
        participant_list = [p.strip() for p in participants.split(',') if p.strip()]

    result = meeting_assistant.start_meeting(title, participant_list)

    # Broadcast meeting start to connected clients
    if result.get('success'):
        await manager.broadcast(json.dumps({
            "type": "meeting_started",
            "data": result
        }))

    return result

@app.post("/api/meeting/stop")
async def stop_meeting():
    """Stop current meeting"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    result = meeting_assistant.stop_meeting()

    # Broadcast meeting stop to connected clients
    if result.get('success'):
        await manager.broadcast(json.dumps({
            "type": "meeting_stopped",
            "data": result
        }))

    return result

@app.get("/api/meeting/status")
async def get_meeting_status():
    """Get current meeting status"""
    if not meeting_assistant:
        return {"active": False, "error": "Meeting assistant not initialized"}

    return meeting_assistant.get_current_meeting_status()

@app.post("/api/transcribe")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribe uploaded audio file"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    try:
        # Save uploaded file temporarily
        temp_dir = Path("data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_file = temp_dir / f"upload_{int(time.time())}_{file.filename}"

        async with aiofiles.open(temp_file, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Transcribe
        result = meeting_assistant.transcribe_audio_file(str(temp_file))

        # Clean up temp file
        temp_file.unlink(missing_ok=True)

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/summarize")
async def summarize_text(text: str = Form(...)):
    """Summarize provided text"""
    if not meeting_assistant:
        return {"success": False, "error": "Meeting assistant not initialized"}

    try:
        result = meeting_assistant.summarize_text(text)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    if not meeting_assistant:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Meeting assistant not initialized"
        })

    status = meeting_assistant.get_engine_status()
    available_engines = {
        "stt": meeting_assistant.get_available_stt_engines(),
        "summarization": meeting_assistant.get_available_summarization_engines()
    }

    return templates.TemplateResponse("settings.html", {
        "request": request,
        "status": status,
        "available_engines": available_engines,
        "config": config
    })

@app.get("/transcribe", response_class=HTMLResponse)
async def transcribe_page(request: Request):
    """Transcription page"""
    return templates.TemplateResponse("transcribe.html", {
        "request": request
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)

    try:
        while True:
            # Send periodic updates
            if meeting_assistant:
                meeting_status = meeting_assistant.get_current_meeting_status()

                if meeting_status.get('active'):
                    await websocket.send_text(json.dumps({
                        "type": "meeting_update",
                        "data": meeting_status
                    }))

            await asyncio.sleep(1)  # Update every second

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    # Create necessary directories
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)

    # Check for environment variable overrides
    host = os.getenv('MEETING_ASSISTANT_HOST', config.server.host)
    port = int(os.getenv('MEETING_ASSISTANT_PORT', config.server.port))
    dev_mode = os.getenv('MEETING_ASSISTANT_DEV', '').lower() in ['1', 'true', 'yes']
    reload = dev_mode if dev_mode else config.server.reload

    print("Starting Meeting Assistant Web Interface...")
    print(f"Server will be available at: http://{host}:{port}")

    uvicorn.run(
        "web_app:app",
        host=host,
        port=port,
        reload=reload
    )