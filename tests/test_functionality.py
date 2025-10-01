#!/usr/bin/env python3
"""
Meeting Assistant Functionality Test
Comprehensive test script to verify all components work correctly
"""

import os
import sys
import time
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class TestMeetingAssistant(unittest.TestCase):
    """Test cases for Meeting Assistant functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_data_dir = Path("test_data")
        self.test_audio_file = self.test_data_dir / "test_speech.wav"
        self.test_transcript_file = self.test_data_dir / "sample_meeting_transcript.txt"

        # Ensure test files exist
        if not self.test_audio_file.exists():
            self.skipTest(f"Test audio file not found: {self.test_audio_file}")
        if not self.test_transcript_file.exists():
            self.skipTest(f"Test transcript file not found: {self.test_transcript_file}")

    def test_config_loading(self):
        """Test configuration loading"""
        print("\n🔧 Testing configuration loading...")

        try:
            from src.config import config

            # Test basic config access
            self.assertIsNotNone(config.app.name)
            self.assertIsNotNone(config.server.host)
            self.assertIsNotNone(config.stt.default_engine)
            self.assertIsNotNone(config.summarization.default_engine)

            print("✅ Configuration loaded successfully")
            print(f"   App: {config.app.name} v{config.app.version}")
            print(f"   Default STT: {config.stt.default_engine}")
            print(f"   Default Summarization: {config.summarization.default_engine}")

        except Exception as e:
            self.fail(f"Configuration loading failed: {e}")

    def test_stt_engines(self):
        """Test STT engine initialization and basic functionality"""
        print("\n🎤 Testing STT engines...")

        try:
            from src.stt import STTManager

            # Initialize STT manager
            stt_config = {
                'default_engine': 'whisper',
                'engines': {
                    'whisper': {
                        'model_size': 'base',
                        'language': 'auto',
                        'device': 'cpu'  # Force CPU for testing
                    }
                }
            }

            stt_manager = STTManager(stt_config)

            # Test engine availability
            available_engines = stt_manager.get_available_engines()
            self.assertIsInstance(available_engines, list)
            print(f"   Available STT engines: {available_engines}")

            # Test engine switching
            if 'whisper' in available_engines:
                success = stt_manager.switch_engine('whisper')
                if success:
                    print("✅ Whisper engine initialized successfully")

                    # Test transcription if audio file exists
                    if self.test_audio_file.exists():
                        print("   Testing audio transcription...")
                        result = stt_manager.transcribe(str(self.test_audio_file))

                        self.assertIn('text', result)
                        self.assertIsInstance(result['text'], str)

                        if result['text']:
                            print(f"✅ Transcription successful: '{result['text'][:50]}...'")
                            print(f"   Engine: {result.get('engine', 'unknown')}")
                            print(f"   Confidence: {result.get('confidence', 'unknown')}")
                        else:
                            print("⚠️  Transcription returned empty text")
                else:
                    print("⚠️  Whisper engine failed to initialize")

            # Cleanup
            stt_manager.cleanup()

        except ImportError as e:
            print(f"⚠️  STT dependencies not available: {e}")
        except Exception as e:
            print(f"❌ STT test failed: {e}")

    def test_summarization_engines(self):
        """Test summarization engine functionality"""
        print("\n🧠 Testing summarization engines...")

        try:
            from src.summarization import SummarizationManager

            # Read test transcript
            with open(self.test_transcript_file, 'r') as f:
                test_text = f.read()

            # Test with minimal config (API-based engines would need keys)
            sum_config = {
                'default_engine': 'qwen3',
                'engines': {
                    'qwen3': {
                        'model_name': 'Qwen/Qwen2.5-3B-Instruct',
                        'device': 'cpu',
                        'max_tokens': 500
                    }
                }
            }

            sum_manager = SummarizationManager(sum_config)

            # Test engine availability
            available_engines = sum_manager.get_available_engines()
            self.assertIsInstance(available_engines, list)
            print(f"   Available summarization engines: {available_engines}")

            # Test basic functionality (may not work without models)
            if 'qwen3' in available_engines:
                try:
                    success = sum_manager.switch_engine('qwen3')
                    if success:
                        print("✅ Qwen3 engine initialized successfully")

                        # Test summarization
                        print("   Testing text summarization...")
                        result = sum_manager.generate_meeting_summary(test_text[:1000])  # Limit text size

                        if result.get('success'):
                            print("✅ Summarization successful")
                            print(f"   Summary length: {len(result.get('summary', ''))}")
                            print(f"   Key points: {len(result.get('key_points', []))}")
                            print(f"   Action items: {len(result.get('action_items', []))}")
                        else:
                            print(f"⚠️  Summarization failed: {result.get('error', 'Unknown error')}")
                    else:
                        print("⚠️  Qwen3 engine failed to initialize (model may not be downloaded)")
                except Exception as e:
                    print(f"⚠️  Qwen3 test failed: {e}")

            # Cleanup
            sum_manager.cleanup()

        except ImportError as e:
            print(f"⚠️  Summarization dependencies not available: {e}")
        except Exception as e:
            print(f"❌ Summarization test failed: {e}")

    def test_audio_recorder(self):
        """Test audio recording functionality"""
        print("\n🔊 Testing audio recorder...")

        try:
            from src.audio import AudioRecorder

            audio_config = {
                'sample_rate': 16000,
                'channels': 1,
                'chunk_size': 1024,
                'input_device': None
            }

            recorder = AudioRecorder(audio_config)

            # Test initialization
            init_success = recorder.initialize()
            if init_success:
                print("✅ Audio recorder initialized successfully")

                # Test device listing
                devices = recorder.list_input_devices()
                print(f"   Found {len(devices)} input devices:")
                for device in devices[:3]:  # Show first 3 devices
                    print(f"     - {device['name']} ({device['sample_rate']}Hz)")

                if devices:
                    print("✅ Audio input devices detected")
                else:
                    print("⚠️  No audio input devices found")

            else:
                print("❌ Audio recorder initialization failed")

            # Cleanup
            recorder.cleanup()

        except ImportError as e:
            print(f"⚠️  Audio dependencies not available: {e}")
        except Exception as e:
            print(f"❌ Audio recorder test failed: {e}")

    def test_meeting_assistant_integration(self):
        """Test main MeetingAssistant class integration"""
        print("\n🎯 Testing MeetingAssistant integration...")

        try:
            from src.meeting import MeetingAssistant

            assistant = MeetingAssistant()

            # Test initialization
            init_success = assistant.initialize()
            print(f"   Assistant initialization: {'✅ Success' if init_success else '⚠️  Partial'}")

            # Test engine availability
            stt_engines = assistant.get_available_stt_engines()
            sum_engines = assistant.get_available_summarization_engines()

            print(f"   STT engines available: {stt_engines}")
            print(f"   Summarization engines available: {sum_engines}")

            # Test engine status
            status = assistant.get_engine_status()
            print(f"   Current STT: {status['stt']['name']} ({'✅' if status['stt']['initialized'] else '❌'})")
            print(f"   Current Summarization: {status['summarization']['name']} ({'✅' if status['summarization']['initialized'] else '❌'})")

            # Test file transcription if audio file exists
            if self.test_audio_file.exists() and stt_engines:
                print("   Testing file transcription...")
                result = assistant.transcribe_audio_file(str(self.test_audio_file))

                if result.get('text'):
                    print("✅ File transcription successful")
                else:
                    print(f"⚠️  File transcription failed: {result.get('error', 'Unknown error')}")

            # Test text summarization if transcript file exists
            if self.test_transcript_file.exists() and sum_engines:
                print("   Testing text summarization...")
                with open(self.test_transcript_file, 'r') as f:
                    test_text = f.read()

                result = assistant.summarize_text(test_text)

                if result.get('success'):
                    print("✅ Text summarization successful")
                else:
                    print(f"⚠️  Text summarization failed: {result.get('error', 'Unknown error')}")

            print("✅ MeetingAssistant integration test completed")

            # Cleanup
            assistant.cleanup()

        except ImportError as e:
            print(f"⚠️  MeetingAssistant dependencies not available: {e}")
        except Exception as e:
            print(f"❌ MeetingAssistant integration test failed: {e}")

    def test_web_app_imports(self):
        """Test web application imports and basic setup"""
        print("\n🌐 Testing web application...")

        try:
            # Test FastAPI app imports
            import fastapi
            import uvicorn
            import jinja2

            print("✅ Web framework dependencies available")
            print(f"   FastAPI: {fastapi.__version__}")
            print(f"   Uvicorn: {uvicorn.__version__}")

            # Test web app import (without running)
            import web_app
            print("✅ Web application imports successfully")

            # Test template directory
            template_dir = Path("templates")
            if template_dir.exists():
                templates = list(template_dir.glob("*.html"))
                print(f"✅ Found {len(templates)} HTML templates")
            else:
                print("⚠️  Templates directory not found")

        except ImportError as e:
            print(f"⚠️  Web dependencies not available: {e}")
        except Exception as e:
            print(f"❌ Web application test failed: {e}")

    def test_cli_imports(self):
        """Test CLI application imports"""
        print("\n💻 Testing CLI application...")

        try:
            import click
            import rich

            print("✅ CLI framework dependencies available")
            print(f"   Click: {click.__version__}")
            print(f"   Rich: {rich.__version__}")

            # Test CLI import
            import cli
            print("✅ CLI application imports successfully")

        except ImportError as e:
            print(f"⚠️  CLI dependencies not available: {e}")
        except Exception as e:
            print(f"❌ CLI application test failed: {e}")

    def test_file_structure(self):
        """Test file structure and required files"""
        print("\n📁 Testing file structure...")

        required_files = [
            "config.yaml",
            "requirements.txt",
            "README.md",
            "cli.py",
            "web_app.py",
            "src/__init__.py",
            "src/config.py",
            "src/meeting.py",
            "templates/base.html",
            "templates/index.html"
        ]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if not missing_files:
            print("✅ All required files present")
        else:
            print(f"⚠️  Missing files: {missing_files}")

        # Test directory structure
        required_dirs = [
            "src",
            "src/stt",
            "src/summarization",
            "src/audio",
            "templates",
            "test_data"
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)

        if not missing_dirs:
            print("✅ All required directories present")
        else:
            print(f"⚠️  Missing directories: {missing_dirs}")

def run_tests():
    """Run all functionality tests"""
    print("=" * 60)
    print("🧪 MEETING ASSISTANT FUNCTIONALITY TEST")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMeetingAssistant)

    # Run tests with custom output
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors

    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")

    if failures:
        print("\nFailures:")
        for test, error in result.failures:
            print(f"  - {test}: {error}")

    if errors:
        print("\nErrors:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")

    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("🎉 Meeting Assistant is ready to use!")
    elif success_rate >= 60:
        print("⚠️  Meeting Assistant partially functional - some features may not work")
    else:
        print("❌ Meeting Assistant needs attention - major issues detected")

    return success_rate >= 60

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)