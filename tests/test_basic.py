#!/usr/bin/env python3
"""
Meeting Assistant Basic Test
Test core functionality without requiring heavy ML dependencies
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_project_structure():
    """Test that all required files and directories exist"""
    print("📁 Testing project structure...")

    required_files = [
        "config.yaml",
        "requirements.txt",
        "README.md",
        "cli.py",
        "web_app.py",
        "src/__init__.py",
        "src/config.py",
        "src/meeting.py",
        "run_test.py",
        "test_data/test_speech.wav",
        "test_data/sample_meeting_transcript.txt"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")

    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False

    print("  ✅ All required files present")
    return True

def test_config_loading():
    """Test configuration loading works"""
    print("\n🔧 Testing configuration...")

    try:
        # Test basic Python imports
        import yaml
        print("  ✅ PyYAML available")

        # Test config loading
        from src.config import config
        print("  ✅ Config module loads")

        # Test config access
        app_name = config.app.name
        server_host = config.server.host
        stt_engine = config.stt.default_engine

        print(f"  ✅ App name: {app_name}")
        print(f"  ✅ Server host: {server_host}")
        print(f"  ✅ Default STT: {stt_engine}")

        return True

    except Exception as e:
        print(f"  ❌ Config test failed: {e}")
        return False

def test_module_structure():
    """Test that modules can be imported (basic structure)"""
    print("\n🏗️ Testing module structure...")

    modules_to_test = [
        ("src.config", "Configuration"),
        ("src.stt.base", "STT Base Classes"),
        ("src.summarization.base", "Summarization Base Classes"),
        ("src.audio", "Audio Module"),
    ]

    success_count = 0
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {description}: {e}")

    print(f"  📊 {success_count}/{len(modules_to_test)} modules loaded")
    return success_count == len(modules_to_test)

def test_scripts_executable():
    """Test that script files are executable"""
    print("\n🔧 Testing script permissions...")

    scripts = [
        "run_test.py",
        "run_cli.sh",
        "run_web.sh",
        "test_setup.sh",
        "install_sbc.sh",
        "install_lightweight.sh"
    ]

    success_count = 0
    for script in scripts:
        script_path = Path(script)
        if script_path.exists():
            if os.access(script_path, os.X_OK):
                print(f"  ✅ {script} is executable")
                success_count += 1
            else:
                print(f"  ⚠️  {script} not executable")
        else:
            print(f"  ❌ {script} missing")

    print(f"  📊 {success_count}/{len(scripts)} scripts ready")
    return success_count >= len(scripts) - 1  # Allow one missing

def test_test_data():
    """Test that test data files are valid"""
    print("\n📊 Testing test data...")

    # Test audio file
    audio_file = Path("test_data/test_speech.wav")
    if audio_file.exists():
        size = audio_file.stat().st_size
        print(f"  ✅ Audio file: {size} bytes")
        audio_ok = size > 1000  # Should be larger than 1KB
    else:
        print("  ❌ Audio file missing")
        audio_ok = False

    # Test transcript file
    transcript_file = Path("test_data/sample_meeting_transcript.txt")
    if transcript_file.exists():
        with open(transcript_file, 'r') as f:
            content = f.read()
        print(f"  ✅ Transcript file: {len(content)} characters")
        transcript_ok = len(content) > 100  # Should have meaningful content
    else:
        print("  ❌ Transcript file missing")
        transcript_ok = False

    return audio_ok and transcript_ok

def test_requirements():
    """Test requirements.txt is valid"""
    print("\n📦 Testing requirements...")

    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("  ❌ requirements.txt missing")
        return False

    try:
        with open(req_file, 'r') as f:
            requirements = f.read().strip().split('\n')

        # Filter out empty lines and comments
        packages = [line for line in requirements if line and not line.startswith('#')]

        print(f"  ✅ Found {len(packages)} package requirements")

        # Check for essential packages
        essential = ['fastapi', 'uvicorn', 'click', 'rich', 'pyyaml']
        found_essential = []

        for pkg in packages:
            pkg_name = pkg.split('==')[0].split('>=')[0].split('<=')[0]
            if pkg_name.lower() in essential:
                found_essential.append(pkg_name)

        print(f"  ✅ Essential packages: {found_essential}")
        return len(found_essential) >= 3  # At least 3 essential packages

    except Exception as e:
        print(f"  ❌ Requirements test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("=" * 50)
    print("🧪 MEETING ASSISTANT BASIC TEST")
    print("=" * 50)
    print("Testing core structure without heavy dependencies...")

    tests = [
        ("Project Structure", test_project_structure),
        ("Configuration", test_config_loading),
        ("Module Structure", test_module_structure),
        ("Script Permissions", test_scripts_executable),
        ("Test Data", test_test_data),
        ("Requirements", test_requirements),
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
    print("📊 BASIC TEST RESULTS")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name:<20} {status}")

    print(f"\nScore: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All basic tests passed! Project structure is correct.")
        print("\nNext steps:")
        print("  ./install_sbc.sh          # Install with local models")
        print("  ./install_lightweight.sh  # Install minimal version")

    elif passed >= total * 0.8:
        print("🟡 Most basic tests passed. Minor issues detected.")

    else:
        print("🔴 Basic tests failed. Project structure needs attention.")

    print("\nAfter installation, run:")
    print("  python3 run_test.py       # Full functionality test")

    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)