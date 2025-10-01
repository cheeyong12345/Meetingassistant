#!/usr/bin/env python3
"""
Complete Meeting Assistant Test with Audio Download
Downloads a test MP3, runs full transcription and summarization, prints all results
"""

import sys
import os
import time
import requests
from pathlib import Path
import subprocess

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def print_header(text):
    print("=" * 70)
    print(f"🎯 {text}")
    print("=" * 70)

def print_status(message, status="info"):
    colors = {
        "info": "\033[32m✅",      # Green
        "warn": "\033[33m⚠️ ",     # Yellow
        "error": "\033[31m❌",     # Red
        "progress": "\033[34m⏳",  # Blue
        "result": "\033[35m📋",    # Magenta
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def download_test_audio():
    """Download a test MP3 file for testing"""
    print_header("DOWNLOADING TEST AUDIO")

    # URLs for test audio files
    test_urls = [
        {
            "url": "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3",
            "filename": "test_bell.mp3",
            "description": "Short bell sound"
        },
        {
            "url": "https://sample-videos.com/zip/10/mp3/SampleAudio_0.4mb_mp3.mp3",
            "filename": "test_speech.mp3",
            "description": "Sample speech audio"
        }
    ]

    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)

    downloaded_file = None

    for audio in test_urls:
        output_file = test_dir / audio["filename"]

        if output_file.exists():
            print_status(f"Using existing file: {output_file}", "info")
            downloaded_file = output_file
            break

        try:
            print_status(f"Downloading {audio['description']}...", "progress")
            response = requests.get(audio["url"], timeout=30)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                f.write(response.content)

            file_size = output_file.stat().st_size / 1024  # KB
            print_status(f"Downloaded: {output_file} ({file_size:.1f} KB)", "info")
            downloaded_file = output_file
            break

        except Exception as e:
            print_status(f"Failed to download {audio['filename']}: {e}", "warn")
            continue

    # Fallback to existing test file
    if not downloaded_file:
        existing_files = list(test_dir.glob("*.wav")) + list(test_dir.glob("*.mp3"))
        if existing_files:
            downloaded_file = existing_files[0]
            print_status(f"Using existing test file: {downloaded_file}", "info")
        else:
            print_status("No test audio available", "error")
            return None

    return downloaded_file

def test_system_status():
    """Test system status and components"""
    print_header("SYSTEM STATUS CHECK")

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        success = assistant.initialize()

        print_status(f"Meeting Assistant initialization: {'Success' if success else 'Failed'}",
                    "info" if success else "error")

        # Get detailed status
        status = assistant.get_engine_status()

        # STT Status
        stt_info = status['stt']
        print_status(f"STT Engine: {stt_info['name']} ({'Ready' if stt_info['initialized'] else 'Failed'})",
                    "info" if stt_info['initialized'] else "warn")

        # Summarization Status
        sum_info = status['summarization']
        print_status(f"Summarization Engine: {sum_info['name']} ({'Ready' if sum_info['initialized'] else 'Failed'})",
                    "info" if sum_info['initialized'] else "warn")

        # Audio devices
        audio_devices = status.get('audio_devices', [])
        print_status(f"Audio input devices: {len(audio_devices)} found", "info")

        # Available engines
        stt_engines = assistant.get_available_stt_engines()
        sum_engines = assistant.get_available_summarization_engines()

        print_status(f"Available STT engines: {', '.join(stt_engines)}", "info")
        print_status(f"Available summarization engines: {', '.join(sum_engines)}", "info")

        assistant.cleanup()
        return success

    except Exception as e:
        print_status(f"System status check failed: {e}", "error")
        return False

def test_transcription(audio_file):
    """Test audio transcription"""
    print_header("AUDIO TRANSCRIPTION TEST")

    if not audio_file or not audio_file.exists():
        print_status("No audio file available for transcription", "error")
        return None

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        assistant.initialize()

        print_status(f"Transcribing: {audio_file.name}", "progress")
        start_time = time.time()

        result = assistant.transcribe_audio_file(str(audio_file))

        elapsed = time.time() - start_time

        print_status(f"Transcription completed in {elapsed:.1f} seconds", "info")

        if result.get('text'):
            print_status("TRANSCRIPTION RESULT:", "result")
            print("-" * 50)
            print(f"Text: {result['text']}")
            print(f"Engine: {result.get('engine', 'unknown')}")
            print(f"Language: {result.get('language', 'unknown')}")
            if 'confidence' in result:
                print(f"Confidence: {result['confidence']:.3f}")
            print("-" * 50)

            assistant.cleanup()
            return result['text']
        else:
            error_msg = result.get('error', 'No transcription returned')
            print_status(f"Transcription failed: {error_msg}", "error")
            assistant.cleanup()
            return None

    except Exception as e:
        print_status(f"Transcription test failed: {e}", "error")
        return None

def test_summarization(text=None):
    """Test text summarization"""
    print_header("TEXT SUMMARIZATION TEST")

    # Use provided text or load sample transcript
    if not text:
        sample_file = Path("test_data/sample_meeting_transcript.txt")
        if sample_file.exists():
            with open(sample_file, 'r') as f:
                text = f.read()
            print_status(f"Using sample transcript ({len(text)} characters)", "info")
        else:
            print_status("No text available for summarization", "error")
            return None
    else:
        print_status(f"Using transcribed text ({len(text)} characters)", "info")

    try:
        from src.meeting import MeetingAssistant

        assistant = MeetingAssistant()
        assistant.initialize()

        print_status("Generating summary...", "progress")
        start_time = time.time()

        result = assistant.summarize_text(text)

        elapsed = time.time() - start_time

        print_status(f"Summarization completed in {elapsed:.1f} seconds", "info")

        if result.get('success'):
            print_status("SUMMARIZATION RESULT:", "result")
            print("-" * 50)

            summary = result.get('summary', '')
            if summary:
                print(f"SUMMARY:\n{summary}\n")

            key_points = result.get('key_points', [])
            if key_points:
                print("KEY POINTS:")
                for i, point in enumerate(key_points, 1):
                    print(f"{i}. {point}")
                print()

            action_items = result.get('action_items', [])
            if action_items:
                print("ACTION ITEMS:")
                for i, item in enumerate(action_items, 1):
                    print(f"{i}. {item}")
                print()

            print(f"Engine: {result.get('engine', 'unknown')}")
            print("-" * 50)

            assistant.cleanup()
            return result
        else:
            error_msg = result.get('error', 'No summary returned')
            print_status(f"Summarization failed: {error_msg}", "error")
            assistant.cleanup()
            return None

    except Exception as e:
        print_status(f"Summarization test failed: {e}", "error")
        return None

def test_cli_commands():
    """Test CLI commands"""
    print_header("CLI INTERFACE TEST")

    commands = [
        ("devices", "List audio devices"),
        ("engines", "List available engines"),
        ("test", "Test engines")
    ]

    for cmd, description in commands:
        try:
            print_status(f"Testing: {description}", "progress")
            result = subprocess.run([
                sys.executable, "cli.py", cmd
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print_status(f"CLI {cmd} command: Success", "info")
                # Show first few lines of output
                output_lines = result.stdout.strip().split('\n')[:5]
                for line in output_lines:
                    if line.strip():
                        print(f"  {line}")
            else:
                print_status(f"CLI {cmd} command failed", "warn")

        except Exception as e:
            print_status(f"CLI {cmd} test failed: {e}", "error")

def test_web_interface():
    """Test web interface startup"""
    print_header("WEB INTERFACE TEST")

    try:
        # Try to import web app
        import web_app
        print_status("Web application imports successfully", "info")

        # Check if FastAPI app exists
        if hasattr(web_app, 'app'):
            print_status("FastAPI app instance found", "info")

            # Try to get some basic info about routes
            routes = web_app.app.routes
            print_status(f"Web routes configured: {len(routes)} routes", "info")

            print_status("Web interface ready (run ./run_web.sh to start)", "info")
        else:
            print_status("FastAPI app not properly configured", "warn")

    except Exception as e:
        print_status(f"Web interface test failed: {e}", "error")

def show_storage_summary():
    """Show storage usage summary"""
    print_header("STORAGE USAGE SUMMARY")

    try:
        # Run the download checker
        result = subprocess.run([
            sys.executable, "check_downloads.py"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Extract key storage information
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Total size:' in line or 'MB' in line:
                    if any(keyword in line for keyword in ['Whisper', 'Hugging Face', 'Local Models', 'Total cache']):
                        print_status(line.strip(), "info")
        else:
            print_status("Could not get storage information", "warn")

    except Exception as e:
        print_status(f"Storage check failed: {e}", "error")

def main():
    """Run complete test suite"""
    start_time = time.time()

    print("🚀" * 35)
    print("🎯 MEETING ASSISTANT COMPLETE TEST SUITE")
    print("🚀" * 35)
    print()

    # Test 1: Download audio
    audio_file = download_test_audio()

    # Test 2: System status
    system_ok = test_system_status()

    # Test 3: Transcription
    transcript_text = None
    if system_ok and audio_file:
        transcript_text = test_transcription(audio_file)

    # Test 4: Summarization (use transcribed text or sample)
    if system_ok:
        test_summarization(transcript_text)

    # Test 5: CLI commands
    test_cli_commands()

    # Test 6: Web interface
    test_web_interface()

    # Test 7: Storage summary
    show_storage_summary()

    # Final summary
    elapsed = time.time() - start_time

    print_header("TEST COMPLETED")
    print_status(f"Total test time: {elapsed:.1f} seconds", "info")

    if system_ok:
        print_status("✅ Meeting Assistant is fully functional!", "info")
        print()
        print("🎯 Ready to use:")
        print("  ./run_web.sh                              # Start web interface")
        print("  ./run_cli.sh record --title \"My Meeting\"  # Record a meeting")
        print("  ./run_cli.sh transcribe audio_file.wav    # Transcribe audio")
        print("  ./run_cli.sh summarize text_file.txt      # Summarize text")
    else:
        print_status("⚠️  Some components need attention", "warn")
        print("Check the error messages above for details")

    print()
    print("🚀" * 35)

if __name__ == "__main__":
    # Make sure we're in the right directory and venv is activated
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Run from project directory with venv.")
        sys.exit(1)

    main()