#!/bin/bash
# Comprehensive diagnostic script for audio device and meeting start issues

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║      Meeting Assistant Diagnostics (RISC-V)                  ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd ~/Meetingassistant

echo "════════════════════════════════════════════════════════════════"
echo "1️⃣  System Audio Devices (ALSA)"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "→ Audio recording devices (arecord):"
arecord -l 2>&1 || echo "arecord not available"
echo ""

echo "→ Audio playback devices (aplay):"
aplay -l 2>&1 || echo "aplay not available"
echo ""

echo "→ ALSA device list:"
cat /proc/asound/cards 2>&1 || echo "ALSA cards info not available"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "2️⃣  PyAudio Device Detection"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "→ Testing PyAudio device enumeration:"
python3 << 'PYTEST'
try:
    import pyaudio
    p = pyaudio.PyAudio()

    print(f"\nTotal devices: {p.get_device_count()}")
    print("\nInput devices:")

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] {info['name']}")
            print(f"      Channels: {info['maxInputChannels']}")
            print(f"      Sample Rate: {int(info['defaultSampleRate'])}")
            print(f"      Host API: {info['hostApi']}")

    p.terminate()
    print("\n✅ PyAudio test completed")

except ImportError:
    print("❌ PyAudio not installed")
except Exception as e:
    print(f"❌ PyAudio error: {e}")
PYTEST
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "3️⃣  Meeting Assistant Audio Recorder Test"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "→ Testing audio recorder initialization:"
python3 << 'PYTEST'
import sys
sys.path.insert(0, '.')

try:
    from src.config import config
    from src.audio.recorder import AudioRecorder

    # Initialize recorder
    audio_config = config.audio.to_dict() if hasattr(config, 'audio') else {}
    recorder = AudioRecorder(audio_config)

    print(f"AudioRecorder created: {recorder is not None}")

    # Initialize
    init_success = recorder.initialize()
    print(f"Initialize success: {init_success}")

    if init_success:
        # List devices
        devices = recorder.list_input_devices()
        print(f"\nDevices found: {len(devices)}")

        for device in devices:
            print(f"  [{device['index']}] {device['name']} ({device['sample_rate']} Hz)")

        recorder.cleanup()
        print("\n✅ Audio recorder test completed")
    else:
        print("\n⚠️  Audio recorder initialization failed")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
PYTEST
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "4️⃣  Web API Endpoints Test"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if web server is running
if pgrep -f "python3.*web_app.py" > /dev/null; then
    echo "✅ Web server is running"
    echo ""

    echo "→ Testing /api/audio-devices endpoint:"
    curl -s http://127.0.0.1:8001/api/audio-devices | python3 -m json.tool 2>&1 || echo "Failed to get audio devices"
    echo ""

    echo "→ Testing /api/status endpoint:"
    curl -s http://127.0.0.1:8001/api/status | python3 -m json.tool 2>&1 || echo "Failed to get status"
    echo ""

    echo "→ Testing /api/meeting/start with empty form:"
    curl -s -X POST http://127.0.0.1:8001/api/meeting/start \
        -F "title=" \
        -F "participants=" 2>&1
    echo ""
    echo ""

else
    echo "❌ Web server is NOT running"
    echo "   Start it with: python3 web_app.py"
    echo ""
fi

echo "════════════════════════════════════════════════════════════════"
echo "5️⃣  Recent Logs"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ -f "logs/meeting_assistant.log" ]; then
    echo "→ Last 30 lines of meeting_assistant.log:"
    tail -30 logs/meeting_assistant.log
    echo ""
else
    echo "⚠️  No log file found"
    echo ""
fi

echo "════════════════════════════════════════════════════════════════"
echo "6️⃣  Configuration Check"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "→ Audio configuration from config.yaml:"
python3 << 'PYTEST'
try:
    from src.config import config

    if hasattr(config, 'audio'):
        audio_conf = config.audio.to_dict()
        import json
        print(json.dumps(audio_conf, indent=2))
    else:
        print("⚠️  No audio section in config")
except Exception as e:
    print(f"❌ Error reading config: {e}")
PYTEST
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ DIAGNOSTICS COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Please copy ALL the output above and paste it back."
echo ""
