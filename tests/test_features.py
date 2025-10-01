#!/usr/bin/env python3
"""
Meeting Assistant Feature Test
Test actual functionality like transcription and summarization
Run this after installation to verify everything works
"""

import sys
import os
import time
import tempfile
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[32m✅",      # Green
        "warn": "\033[33m⚠️ ",     # Yellow
        "error": "\033[31m❌",     # Red
        "test": "\033[36m🧪",      # Cyan
        "progress": "\033[34m⏳",  # Blue
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def check_dependencies():
    """Check if basic dependencies are available"""
    try:
        # Try importing the main module to see if deps are available
        from src.meeting import MeetingAssistant
        return True
    except ImportError:
        return False

def test_meeting_assistant_init():
    """Test Meeting Assistant initialization"""
    print_status("Testing Meeting Assistant initialization...", "test")

    if not check_dependencies():
        print_status("  Core dependencies not installed", "warn")
        return False

    try:
        from src.meeting import MeetingAssistant

        print_status("  Creating Meeting Assistant instance...", "progress")
        assistant = MeetingAssistant()

        print_status("  Initializing assistant...", "progress")
        success = assistant.initialize()

        if success:
            print_status("  Meeting Assistant initialized successfully", "info")
        else:
            print_status("  Meeting Assistant initialization failed", "warn")

        # Get engine status
        status = assistant.get_engine_status()
        stt_status = status['stt']['initialized']
        sum_status = status['summarization']['initialized']

        print_status(f"  STT Engine ({status['stt']['name']}): {'Ready' if stt_status else 'Failed'}",
                    "info" if stt_status else "warn")
        print_status(f"  Summarization Engine ({status['summarization']['name']}): {'Ready' if sum_status else 'Failed'}",
                    "info" if sum_status else "warn")

        # Get available engines
        stt_engines = assistant.get_available_stt_engines()
        sum_engines = assistant.get_available_summarization_engines()

        print_status(f"  Available STT engines: {stt_engines}", "info")
        print_status(f"  Available summarization engines: {sum_engines}", "info")

        assistant.cleanup()
        return success and (stt_status or sum_status)

    except ImportError as e:
        if "whisper" in str(e) or "torch" in str(e) or "fastapi" in str(e):
            print_status("  Dependencies not installed yet", "warn")
            print_status("  Run ./install_sbc.sh or ./install_lightweight.sh first", "warn")
        else:
            print_status(f"  Import error: {e}", "error")
        return False
    except Exception as e:
        print_status(f"  Assistant initialization failed: {e}", "error")
        return False

def test_audio_transcription():
    """Test audio file transcription"""
    print_status("Testing audio transcription...", "test")

    test_audio = Path("test_data/test_speech.wav")
    if not test_audio.exists():
        print_status("  No test audio file found, skipping", "warn")
        return True

    if not check_dependencies():
        print_status("  STT dependencies not installed", "warn")
        return False

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        assistant.initialize()

        print_status(f"  Transcribing {test_audio}...", "progress")
        start_time = time.time()

        result = assistant.transcribe_audio_file(str(test_audio))

        elapsed = time.time() - start_time

        if result.get('text'):
            text = result['text']
            text_preview = text[:100] + "..." if len(text) > 100 else text

            print_status(f"  Transcription successful ({elapsed:.1f}s)", "info")
            print_status(f"  Text: '{text_preview}'", "info")
            print_status(f"  Engine: {result.get('engine', 'unknown')}", "info")
            print_status(f"  Language: {result.get('language', 'unknown')}", "info")

            if 'confidence' in result:
                confidence = result['confidence']
                if isinstance(confidence, (int, float)):
                    print_status(f"  Confidence: {confidence:.2f}", "info")

            assistant.cleanup()
            return True

        else:
            error_msg = result.get('error', 'No text returned')
            print_status(f"  Transcription failed: {error_msg}", "error")
            assistant.cleanup()
            return False

    except ImportError as e:
        if "whisper" in str(e) or "torch" in str(e) or "pyaudio" in str(e):
            print_status("  STT dependencies not installed", "warn")
        else:
            print_status(f"  Import error: {e}", "error")
        return False
    except Exception as e:
        print_status(f"  Transcription test failed: {e}", "error")
        return False

def test_text_summarization():
    """Test text summarization"""
    print_status("Testing text summarization...", "test")

    test_transcript = Path("test_data/sample_meeting_transcript.txt")
    if not test_transcript.exists():
        print_status("  No test transcript file found, skipping", "warn")
        return True

    if not check_dependencies():
        print_status("  Summarization dependencies not installed", "warn")
        return False

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        assistant.initialize()

        # Read test text
        with open(test_transcript, 'r') as f:
            text = f.read()

        print_status(f"  Summarizing {len(text)} characters...", "progress")
        start_time = time.time()

        result = assistant.summarize_text(text)

        elapsed = time.time() - start_time

        if result.get('success'):
            print_status(f"  Summarization successful ({elapsed:.1f}s)", "info")

            summary = result.get('summary', '')
            key_points = result.get('key_points', [])
            action_items = result.get('action_items', [])

            if summary:
                summary_preview = summary[:150] + "..." if len(summary) > 150 else summary
                print_status(f"  Summary: '{summary_preview}'", "info")

            print_status(f"  Key points found: {len(key_points)}", "info")
            for i, point in enumerate(key_points[:3]):  # Show first 3
                print_status(f"    {i+1}. {point}", "info")

            print_status(f"  Action items found: {len(action_items)}", "info")
            for i, item in enumerate(action_items[:3]):  # Show first 3
                print_status(f"    {i+1}. {item}", "info")

            assistant.cleanup()
            return True

        else:
            error_msg = result.get('error', 'No summary returned')
            print_status(f"  Summarization failed: {error_msg}", "error")
            assistant.cleanup()
            return False

    except ImportError as e:
        if "torch" in str(e) or "transformers" in str(e) or "ollama" in str(e):
            print_status("  Summarization dependencies not installed", "warn")
        else:
            print_status(f"  Import error: {e}", "error")
        return False
    except Exception as e:
        print_status(f"  Summarization test failed: {e}", "error")
        return False

def test_engine_switching():
    """Test switching between different engines"""
    print_status("Testing engine switching...", "test")

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        assistant.initialize()

        # Test STT engine switching
        stt_engines = assistant.get_available_stt_engines()
        stt_switched = 0

        for engine in stt_engines:
            print_status(f"  Switching to STT engine: {engine}", "progress")
            if assistant.switch_stt_engine(engine):
                print_status(f"    Successfully switched to {engine}", "info")
                stt_switched += 1
            else:
                print_status(f"    Failed to switch to {engine}", "warn")

        # Test summarization engine switching
        sum_engines = assistant.get_available_summarization_engines()
        sum_switched = 0

        for engine in sum_engines:
            print_status(f"  Switching to summarization engine: {engine}", "progress")
            if assistant.switch_summarization_engine(engine):
                print_status(f"    Successfully switched to {engine}", "info")
                sum_switched += 1
            else:
                print_status(f"    Failed to switch to {engine}", "warn")

        print_status(f"  STT engines working: {stt_switched}/{len(stt_engines)}", "info")
        print_status(f"  Summarization engines working: {sum_switched}/{len(sum_engines)}", "info")

        assistant.cleanup()
        return (stt_switched > 0) and (sum_switched > 0)

    except ImportError as e:
        print_status("  Engine dependencies not installed", "warn")
        return False
    except Exception as e:
        print_status(f"  Engine switching test failed: {e}", "error")
        return False

def test_audio_devices():
    """Test audio device detection and basic recording setup"""
    print_status("Testing audio device detection...", "test")

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        assistant.initialize()

        status = assistant.get_engine_status()
        audio_devices = status.get('audio_devices', [])

        print_status(f"  Found {len(audio_devices)} audio input devices", "info")

        for i, device in enumerate(audio_devices[:5]):  # Show first 5
            name = device.get('name', 'Unknown')
            sample_rate = device.get('sample_rate', 'Unknown')
            print_status(f"    {i}: {name} ({sample_rate}Hz)", "info")

        assistant.cleanup()
        return len(audio_devices) > 0

    except ImportError as e:
        print_status("  Audio dependencies not installed", "warn")
        return False
    except Exception as e:
        print_status(f"  Audio device test failed: {e}", "error")
        return False

def test_web_app_import():
    """Test web application can be imported"""
    print_status("Testing web application import...", "test")

    try:
        import web_app
        print_status("  Web application imports successfully", "info")

        # Check if FastAPI app is created
        if hasattr(web_app, 'app'):
            print_status("  FastAPI app instance found", "info")
            return True
        else:
            print_status("  FastAPI app instance not found", "warn")
            return False

    except ImportError as e:
        if "fastapi" in str(e) or "uvicorn" in str(e):
            print_status("  Web dependencies not installed", "warn")
        else:
            print_status(f"  Import error: {e}", "error")
        return False
    except Exception as e:
        print_status(f"  Web app import failed: {e}", "error")
        return False

def test_cli_import():
    """Test CLI application can be imported"""
    print_status("Testing CLI application import...", "test")

    try:
        import cli
        print_status("  CLI application imports successfully", "info")

        # Check if click commands are defined
        if hasattr(cli, 'cli'):
            print_status("  Click CLI group found", "info")
            return True
        else:
            print_status("  Click CLI group not found", "warn")
            return False

    except ImportError as e:
        if "whisper" in str(e) or "click" in str(e):
            print_status("  CLI dependencies not installed", "warn")
        else:
            print_status(f"  Import error: {e}", "error")
        return False
    except Exception as e:
        print_status(f"  CLI import failed: {e}", "error")
        return False

def main():
    """Run all feature tests"""
    start_time = time.time()

    print("=" * 70)
    print("🚀 MEETING ASSISTANT FEATURE TEST")
    print("=" * 70)
    print("Testing actual functionality after installation...")
    print()

    # Run all tests
    tests = [
        ("Meeting Assistant Init", test_meeting_assistant_init),
        ("Audio Transcription", test_audio_transcription),
        ("Text Summarization", test_text_summarization),
        ("Engine Switching", test_engine_switching),
        ("Audio Device Detection", test_audio_devices),
        ("Web Application", test_web_app_import),
        ("CLI Application", test_cli_import),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print_status(f"Running {test_name} test...", "test")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test {test_name} crashed: {e}", "error")
            results.append((test_name, False))
        print()

    # Summary
    print("=" * 70)
    print("📊 FEATURE TEST RESULTS")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        status_text = "PASS" if result else "FAIL"
        print(f"{status_icon} {test_name:<25} {status_text}")
        if result:
            passed += 1

    percentage = (passed / total * 100) if total > 0 else 0
    elapsed = time.time() - start_time

    print()
    print(f"Overall Score: {passed}/{total} ({percentage:.1f}%)")
    print(f"Test completed in {elapsed:.1f} seconds")

    print()

    # Recommendations
    if percentage >= 85:
        print("🎉 Excellent! Meeting Assistant is fully functional.")
        print()
        print("You can now:")
        print("  ./run_web.sh                              # Start web interface")
        print("  ./run_cli.sh record --title \"My Meeting\"  # Record a meeting")
        print("  ./run_cli.sh transcribe audio_file.wav    # Transcribe audio")

    elif percentage >= 70:
        print("🟢 Good! Most features are working.")
        print("Some optional features may need attention.")

    elif percentage >= 50:
        print("🟡 Partial functionality. Core features work.")
        print("Consider reinstalling or checking model downloads.")

    else:
        print("🔴 Dependencies not installed or major issues detected.")
        print()
        if passed == 0:
            print("It looks like you haven't run the installation yet.")
            print("Try:")
            print("  ./install_sbc.sh          # Full installation with local models")
            print("  ./install_lightweight.sh  # Minimal installation with API-based services")
        else:
            print("Some components are working but others have issues.")
            print("Try:")
            print("  ./install_sbc.sh          # Reinstall with models")
            print("  python3 quick_test.py     # Check what's missing")

    return percentage >= 50

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)