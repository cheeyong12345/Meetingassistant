#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing imports...")
print("=" * 50)

try:
    print("1. Testing config import...")
    from src.config import config
    print("   ✓ Config imported successfully")
except Exception as e:
    print(f"   ✗ Config import failed: {e}")
    sys.exit(1)

try:
    print("2. Testing meeting import...")
    from src.meeting import MeetingAssistant
    print("   ✓ MeetingAssistant imported successfully")
except Exception as e:
    print(f"   ✗ MeetingAssistant import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing STT imports...")
    from src.stt import STTManager
    print("   ✓ STTManager imported successfully")
except Exception as e:
    print(f"   ✗ STTManager import failed: {e}")
    sys.exit(1)

try:
    print("4. Testing summarization imports...")
    from src.summarization import SummarizationManager
    print("   ✓ SummarizationManager imported successfully")
except Exception as e:
    print(f"   ✗ SummarizationManager import failed: {e}")
    sys.exit(1)

try:
    print("5. Testing audio imports...")
    from src.audio import AudioRecorder
    print("   ✓ AudioRecorder imported successfully")
except Exception as e:
    print(f"   ✗ AudioRecorder import failed: {e}")
    sys.exit(1)

print("=" * 50)
print("All imports successful!")
print("")
print("The application is ready to run.")
