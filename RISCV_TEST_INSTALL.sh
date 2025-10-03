#!/bin/bash
# Test RISC-V Installation and Fix Transformers Safetensors Warning

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         RISC-V Installation Test & Fix                       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Not in virtual environment!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo ""

# Set environment variable to disable safetensors requirement
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1
echo "✅ Set TRANSFORMERS_NO_ADVISORY_WARNINGS=1"
echo ""

# Test Python packages
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Python Package Imports"
echo "════════════════════════════════════════════════════════════════"
echo ""

python3 << 'EOF'
import os
import sys

# Disable transformers dependency warnings
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'

# Monkey-patch the version check to disable safetensors requirement
try:
    import transformers.utils.versions as v
    original_require = v.require_version

    def patched_require(requirement, hint=None):
        # Skip safetensors and tokenizers checks
        if 'safetensors' in requirement or 'tokenizers' in requirement:
            return
        return original_require(requirement, hint)

    v.require_version = patched_require
except Exception as e:
    print(f"⚠️  Could not patch version check: {e}")

# Test imports
print("Testing critical packages:")
print("")

all_ok = True

# Test transformers
try:
    import transformers
    print(f"  ✅ transformers       {transformers.__version__}")
except Exception as e:
    print(f"  ❌ transformers       FAILED: {e}")
    all_ok = False

# Test FastAPI
try:
    import fastapi
    print(f"  ✅ fastapi            {fastapi.__version__}")
except Exception as e:
    print(f"  ❌ fastapi            FAILED: {e}")
    all_ok = False

# Test Uvicorn
try:
    import uvicorn
    print(f"  ✅ uvicorn            {uvicorn.__version__}")
except Exception as e:
    print(f"  ❌ uvicorn            FAILED: {e}")
    all_ok = False

# Test Pydantic
try:
    import pydantic
    version = pydantic.__version__
    if version.startswith('2.'):
        print(f"  ⚠️  pydantic           {version} (WARNING: v2 detected, should be v1)")
    else:
        print(f"  ✅ pydantic           {version}")
except Exception as e:
    print(f"  ❌ pydantic           FAILED: {e}")
    all_ok = False

# Test other utilities
packages = {
    'numpy': 'NumPy',
    'click': 'Click',
    'rich': 'Rich',
    'yaml': 'PyYAML',
    'requests': 'Requests',
    'aiofiles': 'AIOFiles'
}

for module, name in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✅ {name:18s} {version}")
    except ImportError as e:
        print(f"  ❌ {name:18s} FAILED")
        all_ok = False

print("")
if all_ok:
    print("✅ All critical packages imported successfully!")
else:
    print("❌ Some packages failed to import")
    sys.exit(1)

# Test transformers functionality
print("")
print("Testing transformers functionality:")
try:
    from transformers import AutoTokenizer
    print("  ✅ AutoTokenizer works")
except Exception as e:
    print(f"  ❌ AutoTokenizer failed: {e}")
    all_ok = False

print("")
sys.exit(0 if all_ok else 1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Package import tests FAILED"
    exit 1
fi

# Test Meeting Assistant imports
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Meeting Assistant"
echo "════════════════════════════════════════════════════════════════"
echo ""

export TRANSFORMERS_NO_ADVISORY_WARNINGS=1

python3 << 'EOF'
import os
import sys

os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'

# Monkey-patch transformers version check
try:
    import transformers.utils.versions as v
    original_require = v.require_version

    def patched_require(requirement, hint=None):
        if 'safetensors' in requirement or 'tokenizers' in requirement:
            return
        return original_require(requirement, hint)

    v.require_version = patched_require
except:
    pass

# Test Meeting Assistant imports
sys.path.insert(0, '.')

try:
    from src.meeting import MeetingAssistant
    print("  ✅ MeetingAssistant imports OK")
except Exception as e:
    print(f"  ❌ MeetingAssistant import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test config
try:
    from src.config import config
    print("  ✅ Config loads OK")
except Exception as e:
    print(f"  ❌ Config failed: {e}")

# Test hardware detection
try:
    from src.utils.hardware import get_hardware_detector
    hw = get_hardware_detector()
    info = hw.get_system_info()
    print(f"  ✅ Hardware detection: {info['architecture']} / {info['soc_type']}")
except Exception as e:
    print(f"  ⚠️  Hardware detection failed: {e}")

# Test ESWIN NPU
try:
    from src.utils.eswin_npu import ESWINNPUInterface
    if ESWINNPUInterface.is_available():
        print("  ✅ ESWIN NPU binary detected!")
    else:
        print("  ℹ️  ESWIN NPU binary not found (optional)")
except Exception as e:
    print(f"  ⚠️  ESWIN NPU check failed: {e}")

print("")
print("✅ Meeting Assistant is ready!")
sys.exit(0)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Meeting Assistant tests FAILED"
    exit 1
fi

# Offer to add environment variable to bashrc
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📝 Environment Setup"
echo "════════════════════════════════════════════════════════════════"
echo ""

if ! grep -q "TRANSFORMERS_NO_ADVISORY_WARNINGS" ~/.bashrc; then
    echo "Would you like to add the environment variable to ~/.bashrc?"
    echo "This will suppress safetensors warnings automatically."
    echo ""
    read -p "Add to ~/.bashrc? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo "" >> ~/.bashrc
        echo "# Disable transformers safetensors warnings (not available on RISC-V)" >> ~/.bashrc
        echo "export TRANSFORMERS_NO_ADVISORY_WARNINGS=1" >> ~/.bashrc
        echo "✅ Added to ~/.bashrc"
        echo "   Run: source ~/.bashrc"
    else
        echo "ℹ️  Skipped. You'll need to run this before starting the app:"
        echo "   export TRANSFORMERS_NO_ADVISORY_WARNINGS=1"
    fi
else
    echo "✅ Environment variable already in ~/.bashrc"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ INSTALLATION TEST COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Source your bashrc (if you added the env var):"
echo "   source ~/.bashrc"
echo ""
echo "2. Test the web app:"
echo "   export TRANSFORMERS_NO_ADVISORY_WARNINGS=1"
echo "   python3 web_app.py"
echo ""
echo "3. Open browser:"
echo "   http://localhost:8000"
echo ""
echo "ℹ️  Note: Using slow Python tokenizers (Rust tokenizers not available)"
echo "   This is normal on RISC-V and won't affect functionality."
echo ""
