#!/usr/bin/env python3
"""
Quick Component Test for Meeting Assistant
Fast verification of all components without heavy model loading
"""

import sys
import os
import time
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
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')} {message}{reset}")

def test_core_imports():
    """Test core Python imports"""
    print_status("Testing core imports...", "test")

    tests = [
        ("os, sys, pathlib", lambda: __import__('os') and __import__('sys') and __import__('pathlib')),
        ("yaml", lambda: __import__('yaml')),
        ("json", lambda: __import__('json')),
        ("time, datetime", lambda: __import__('time') and __import__('datetime')),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print_status(f"  {name}", "info")
            passed += 1
        except ImportError:
            print_status(f"  {name} - MISSING", "error")

    return passed, len(tests)

def test_web_framework():
    """Test web framework components"""
    print_status("Testing web framework...", "test")

    tests = [
        ("fastapi", lambda: __import__('fastapi')),
        ("uvicorn", lambda: __import__('uvicorn')),
        ("jinja2", lambda: __import__('jinja2')),
        ("aiofiles", lambda: __import__('aiofiles')),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print_status(f"  {name}", "info")
            passed += 1
        except ImportError:
            print_status(f"  {name} - MISSING", "error")

    return passed, len(tests)

def test_cli_framework():
    """Test CLI framework components"""
    print_status("Testing CLI framework...", "test")

    tests = [
        ("click", lambda: __import__('click')),
        ("rich", lambda: __import__('rich')),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            module = test_func()
            version = getattr(module, '__version__', 'unknown')
            print_status(f"  {name} ({version})", "info")
            passed += 1
        except ImportError:
            print_status(f"  {name} - MISSING", "error")

    return passed, len(tests)

def test_audio_framework():
    """Test audio processing components"""
    print_status("Testing audio framework...", "test")

    tests = [
        ("pyaudio", lambda: __import__('pyaudio')),
        ("pydub", lambda: __import__('pydub')),
        ("numpy", lambda: __import__('numpy')),
        ("scipy", lambda: __import__('scipy')),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print_status(f"  {name}", "info")
            passed += 1
        except ImportError:
            print_status(f"  {name} - MISSING", "error")

    return passed, len(tests)

def test_stt_engines():
    """Test STT engine availability"""
    print_status("Testing STT engines...", "test")

    tests = [
        ("whisper", lambda: __import__('whisper')),
        ("speech_recognition", lambda: __import__('speech_recognition')),
        ("vosk", lambda: __import__('vosk')),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print_status(f"  {name}", "info")
            passed += 1
        except ImportError:
            print_status(f"  {name} - MISSING", "warn")

    return passed, len(tests)

def test_ai_engines():
    """Test AI/ML engine availability"""
    print_status("Testing AI engines...", "test")

    tests = [
        ("torch", lambda: __import__('torch')),
        ("transformers", lambda: __import__('transformers')),
        ("ollama", lambda: __import__('ollama')),
    ]

    passed = 0
    for name, test_func in tests:
        try:
            test_func()
            print_status(f"  {name}", "info")
            passed += 1
        except ImportError:
            print_status(f"  {name} - MISSING", "warn")

    return passed, len(tests)

def test_config_loading():
    """Test configuration system"""
    print_status("Testing configuration...", "test")

    try:
        from src.config import config

        # Test basic config access
        app_name = config.app.name
        server_host = config.server.host
        stt_engine = config.stt.default_engine
        sum_engine = config.summarization.default_engine

        print_status(f"  App: {app_name}", "info")
        print_status(f"  Server: {server_host}:{config.server.port}", "info")
        print_status(f"  Default STT: {stt_engine}", "info")
        print_status(f"  Default AI: {sum_engine}", "info")

        return 1, 1

    except Exception as e:
        print_status(f"  Config loading failed: {e}", "error")
        return 0, 1

def test_module_structure():
    """Test internal module structure"""
    print_status("Testing module structure...", "test")

    modules = [
        "src.config",
        "src.meeting",
    ]

    # Test modules that don't require heavy dependencies
    light_modules = [
        ("src.stt.base", "STT base classes"),
        ("src.summarization.base", "Summarization base classes"),
        ("src.audio", "Audio recorder"),
    ]

    passed = 0
    total = len(modules) + len(light_modules)

    # Test basic modules
    for module in modules:
        try:
            __import__(module)
            print_status(f"  {module}", "info")
            passed += 1
        except ImportError as e:
            print_status(f"  {module} - {e}", "error")

    # Test light modules
    for module, description in light_modules:
        try:
            __import__(module)
            print_status(f"  {description}", "info")
            passed += 1
        except ImportError:
            print_status(f"  {description} - dependencies missing", "warn")

    return passed, total

def test_file_structure():
    """Test required files and directories"""
    print_status("Testing file structure...", "test")

    required_files = [
        "config.yaml",
        "requirements.txt",
        "README.md",
        "cli.py",
        "web_app.py",
        "test_data/test_speech.wav",
        "test_data/sample_meeting_transcript.txt"
    ]

    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
        else:
            print_status(f"  {file_path}", "info")

    if missing:
        for file_path in missing:
            print_status(f"  {file_path} - MISSING", "error")

    return len(required_files) - len(missing), len(required_files)

def test_scripts_executable():
    """Test script executability"""
    print_status("Testing script permissions...", "test")

    scripts = [
        "run_cli.py",
        "run_web.py",
        "test_setup.py",
        "install_sbc.py",
        "install_lightweight.py",
        "test.py",
        "quick_test.py"
    ]

    executable = 0
    for script in scripts:
        script_path = Path(script)
        if script_path.exists() and os.access(script_path, os.X_OK):
            print_status(f"  {script}", "info")
            executable += 1
        else:
            print_status(f"  {script} - not executable", "warn")

    return executable, len(scripts)

def test_audio_devices():
    """Test audio device detection (quick check)"""
    print_status("Testing audio devices...", "test")

    try:
        import pyaudio
        pa = pyaudio.PyAudio()

        device_count = pa.get_device_count()
        input_devices = 0

        for i in range(device_count):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices += 1

        pa.terminate()

        print_status(f"  Found {input_devices} input devices", "info")
        return 1 if input_devices > 0 else 0, 1

    except ImportError:
        print_status("  PyAudio not available", "warn")
        return 0, 1
    except Exception as e:
        print_status(f"  Audio test failed: {e}", "warn")
        return 0, 1

def main():
    """Run all quick tests"""
    start_time = time.time()

    print("=" * 60)
    print("🚀 MEETING ASSISTANT QUICK COMPONENT TEST")
    print("=" * 60)
    print()

    # Run all tests
    tests = [
        ("Core Imports", test_core_imports),
        ("Web Framework", test_web_framework),
        ("CLI Framework", test_cli_framework),
        ("Audio Framework", test_audio_framework),
        ("STT Engines", test_stt_engines),
        ("AI Engines", test_ai_engines),
        ("Configuration", test_config_loading),
        ("Module Structure", test_module_structure),
        ("File Structure", test_file_structure),
        ("Script Permissions", test_scripts_executable),
        ("Audio Devices", test_audio_devices),
    ]

    all_results = []

    for test_name, test_func in tests:
        try:
            passed, total = test_func()
            all_results.append((test_name, passed, total))
        except Exception as e:
            print_status(f"Test {test_name} crashed: {e}", "error")
            all_results.append((test_name, 0, 1))
        print()

    # Summary
    print("=" * 60)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 60)

    total_passed = 0
    total_tests = 0

    for test_name, passed, total in all_results:
        percentage = (passed / total * 100) if total > 0 else 0
        status_icon = "✅" if percentage == 100 else "⚠️" if percentage > 50 else "❌"
        print(f"{status_icon} {test_name:<20} {passed}/{total} ({percentage:.0f}%)")
        total_passed += passed
        total_tests += total

    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print()
    print(f"Overall Score: {total_passed}/{total_tests} ({overall_percentage:.1f}%)")

    elapsed = time.time() - start_time
    print(f"Test completed in {elapsed:.1f} seconds")

    print()

    # Recommendations
    if overall_percentage >= 90:
        print("🎉 Excellent! All components are ready.")
        print("You can use all features of Meeting Assistant.")

    elif overall_percentage >= 75:
        print("🟢 Good! Most components are working.")
        print("Some optional features may not be available.")

    elif overall_percentage >= 50:
        print("🟡 Partial setup. Basic functionality should work.")
        print("Install missing dependencies for full functionality.")

    else:
        print("🔴 Many components missing. Run installation first.")

    print()
    print("Next steps:")
    if overall_percentage < 75:
        print("  python3 install_sbc.py         # Full installation")
        print("  python3 install_lightweight.py # Minimal installation")
    print("  python3 run_web.py             # Start web interface")
    print("  python3 run_test.py            # Full functionality test")

    return overall_percentage >= 50

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)