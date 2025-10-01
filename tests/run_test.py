#!/usr/bin/env python3
"""
Meeting Assistant Quick Test Runner
Simple test to verify basic functionality works
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("🔧 Testing imports...")

    try:
        # Test core imports
        import yaml
        import click
        import rich
        print("  ✅ Core dependencies")

        # Test config
        from src.config import config
        print(f"  ✅ Config loaded: {config.app.name}")

        # Test STT
        from src.stt import STTManager
        print("  ✅ STT module")

        # Test summarization
        from src.summarization import SummarizationManager
        print("  ✅ Summarization module")

        # Test audio
        from src.audio import AudioRecorder
        print("  ✅ Audio module")

        # Test main assistant
        from src.meeting import MeetingAssistant
        print("  ✅ Meeting Assistant")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without heavy models"""
    print("\n🎯 Testing basic functionality...")

    try:
        from src.meeting import MeetingAssistant

        # Create assistant
        assistant = MeetingAssistant()

        # Test engine listing
        stt_engines = assistant.get_available_stt_engines()
        sum_engines = assistant.get_available_summarization_engines()

        print(f"  ✅ STT engines detected: {stt_engines}")
        print(f"  ✅ Summarization engines detected: {sum_engines}")

        # Test status
        status = assistant.get_engine_status()
        print(f"  ✅ Engine status retrieved")

        # Test audio device listing
        audio_devices = status.get('audio_devices', [])
        print(f"  ✅ Audio devices found: {len(audio_devices)}")

        assistant.cleanup()
        return True

    except Exception as e:
        print(f"  ❌ Functionality test failed: {e}")
        return False

def test_transcription():
    """Test transcription with sample audio if available"""
    print("\n🎤 Testing transcription...")

    test_audio = Path("test_data/test_speech.wav")

    if not test_audio.exists():
        print("  ⚠️  No test audio file, skipping transcription test")
        return True

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()

        # Try to initialize with basic engines
        init_success = assistant.initialize()

        if not init_success:
            print("  ⚠️  Assistant initialization failed, transcription may not work")

        # Test transcription
        print(f"  🔄 Transcribing {test_audio}...")
        result = assistant.transcribe_audio_file(str(test_audio))

        if result.get('text'):
            text = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
            print(f"  ✅ Transcription successful: '{text}'")
            print(f"     Engine: {result.get('engine', 'unknown')}")
            success = True
        else:
            print(f"  ❌ Transcription failed: {result.get('error', 'No text returned')}")
            success = False

        assistant.cleanup()
        return success

    except Exception as e:
        print(f"  ❌ Transcription test error: {e}")
        return False

def test_summarization():
    """Test summarization with sample text"""
    print("\n🧠 Testing summarization...")

    test_transcript = Path("test_data/sample_meeting_transcript.txt")

    if not test_transcript.exists():
        print("  ⚠️  No test transcript file, skipping summarization test")
        return True

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()

        # Read test text
        with open(test_transcript, 'r') as f:
            text = f.read()

        print(f"  🔄 Summarizing {len(text)} characters...")
        result = assistant.summarize_text(text)

        if result.get('success'):
            summary = result.get('summary', '')
            key_points = result.get('key_points', [])
            action_items = result.get('action_items', [])

            print(f"  ✅ Summarization successful")
            print(f"     Summary length: {len(summary)}")
            print(f"     Key points: {len(key_points)}")
            print(f"     Action items: {len(action_items)}")

            if summary:
                preview = summary[:100] + "..." if len(summary) > 100 else summary
                print(f"     Preview: '{preview}'")

            success = True
        else:
            print(f"  ❌ Summarization failed: {result.get('error', 'No summary returned')}")
            success = False

        assistant.cleanup()
        return success

    except Exception as e:
        print(f"  ❌ Summarization test error: {e}")
        return False

def test_web_app():
    """Test web app can be imported and basic setup"""
    print("\n🌐 Testing web application...")

    try:
        # Test web framework imports
        import fastapi
        import uvicorn
        print("  ✅ Web framework available")

        # Test web app import
        import web_app
        print("  ✅ Web app imports successfully")

        # Check templates
        template_dir = Path("templates")
        if template_dir.exists():
            templates = list(template_dir.glob("*.html"))
            print(f"  ✅ Templates found: {len(templates)}")
        else:
            print("  ⚠️  Templates directory missing")

        return True

    except ImportError as e:
        print(f"  ❌ Web dependencies missing: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Web test error: {e}")
        return False

def test_cli_app():
    """Test CLI app can be imported"""
    print("\n💻 Testing CLI application...")

    try:
        import cli
        print("  ✅ CLI app imports successfully")
        return True

    except ImportError as e:
        print(f"  ❌ CLI dependencies missing: {e}")
        return False
    except Exception as e:
        print(f"  ❌ CLI test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 MEETING ASSISTANT QUICK TEST")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Transcription", test_transcription),
        ("Summarization", test_summarization),
        ("Web Application", test_web_app),
        ("CLI Application", test_cli_app),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name:<20} {status}")

    print(f"\nScore: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Meeting Assistant is ready to use.")
        print("\nNext steps:")
        print("  ./run_web.sh                    # Start web interface")
        print("  ./run_cli.sh test               # Detailed CLI test")
        print("  ./run_cli.sh transcribe test_data/test_speech.wav")

    elif passed >= total * 0.8:
        print("🟡 Most tests passed. Some features may need attention.")
        print("\nYou can still use the basic functionality.")

    else:
        print("🔴 Many tests failed. Check installation and dependencies.")
        print("\nTry running:")
        print("  ./install_sbc.sh                # Full installation")
        print("  ./install_lightweight.sh        # Minimal installation")

    return passed >= total * 0.6

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)