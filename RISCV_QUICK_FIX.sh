#!/bin/bash
# Quick Fix Script for RISC-V Installation
# Handles packages that don't have RISC-V wheels

# Don't exit on error - we want to continue and report all issues
set +e

LOG_FILE="/tmp/riscv_install_$(date +%Y%m%d_%H%M%S).log"
FAILED_PACKAGES=()
SUCCESS_PACKAGES=()

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         RISC-V Quick Fix - Install Compatible Versions       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Logging to: $LOG_FILE"
echo ""

# Check if in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not in virtual environment"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: $VIRTUAL_ENV"
echo "🏗️  Architecture: $(uname -m)"
echo ""

# Helper function to install package
install_pkg() {
    local pkg=$1
    local desc=$2
    local optional=${3:-no}

    echo "→ Installing $desc..."
    echo "====== Installing $pkg @ $(date) ======" >> "$LOG_FILE"

    if pip install --no-cache-dir $pkg >> "$LOG_FILE" 2>&1; then
        echo "   ✅ $desc installed successfully"
        SUCCESS_PACKAGES+=("$desc")
        return 0
    else
        if [ "$optional" = "yes" ]; then
            echo "   ⚠️  $desc failed (optional - skipping)"
        else
            echo "   ❌ $desc FAILED - see log for details"
            FAILED_PACKAGES+=("$desc")
        fi
        echo "====== FAILED ======" >> "$LOG_FILE"
        return 1
    fi
}

echo "📦 Installing packages compatible with RISC-V..."
echo ""

# Critical packages first
install_pkg "\"pydantic<2.0\"" "Pydantic v1 (no Rust required)"
install_pkg "uvicorn" "Uvicorn (ASGI server)"
install_pkg "jinja2" "Jinja2 (templating)"
install_pkg "python-multipart" "Python Multipart"
install_pkg "python-socketio" "Python SocketIO"
install_pkg "fastapi" "FastAPI (without all extras to avoid Rust deps)"
install_pkg "click" "Click (CLI framework)"
install_pkg "rich" "Rich (terminal formatting)"

# Transformers without tokenizers (to avoid Rust)
echo "→ Installing Transformers (without tokenizers to avoid Rust)..."
echo "====== Installing transformers (no-deps) @ $(date) ======" >> "$LOG_FILE"
if pip install --no-cache-dir --no-deps transformers >> "$LOG_FILE" 2>&1; then
    # Now install only the dependencies that don't need Rust
    pip install --no-cache-dir filelock huggingface-hub packaging regex requests tqdm >> "$LOG_FILE" 2>&1
    echo "   ✅ Transformers installed (using slow Python tokenizers)"
    SUCCESS_PACKAGES+=("Transformers (no Rust tokenizers)")
else
    echo "   ❌ Transformers FAILED - see log for details"
    FAILED_PACKAGES+=("Transformers")
    echo "====== FAILED ======" >> "$LOG_FILE"
fi

# Optional packages (skip Rust-dependent ones)
install_pkg "sentencepiece" "SentencePiece (tokenization)" "yes"
install_pkg "protobuf" "Protocol Buffers" "yes"

# Utilities
install_pkg "pyyaml" "PyYAML"
install_pkg "requests" "Requests"
install_pkg "aiofiles" "AIOFiles"
install_pkg "sqlalchemy" "SQLAlchemy"
install_pkg "python-dotenv" "Python Dotenv"

# Audio libraries (optional, need libffi-dev)
echo ""
echo "→ Checking for libffi-dev (needed for audio libraries)..."
if ! dpkg -l | grep -q libffi-dev; then
    echo "   Installing libffi-dev..."
    if sudo apt install -y libffi-dev >> "$LOG_FILE" 2>&1; then
        echo "   ✅ libffi-dev installed"
    else
        echo "   ⚠️  libffi-dev install failed (may need sudo)"
    fi
else
    echo "   ✅ libffi-dev already installed"
fi

install_pkg "pydub" "Pydub (audio processing)" "yes"
install_pkg "soundfile" "SoundFile (audio I/O)" "yes"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 Installation Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Report results
if [ ${#SUCCESS_PACKAGES[@]} -gt 0 ]; then
    echo "✅ Successfully installed (${#SUCCESS_PACKAGES[@]}):"
    for pkg in "${SUCCESS_PACKAGES[@]}"; do
        echo "   ✓ $pkg"
    done
    echo ""
fi

if [ ${#FAILED_PACKAGES[@]} -gt 0 ]; then
    echo "❌ Failed to install (${#FAILED_PACKAGES[@]}):"
    for pkg in "${FAILED_PACKAGES[@]}"; do
        echo "   ✗ $pkg"
    done
    echo ""
    echo "📝 Check log file for details: $LOG_FILE"
    echo "   Last 20 lines:"
    tail -20 "$LOG_FILE" | sed 's/^/   /'
    echo ""
fi

# Verify actual imports
echo "════════════════════════════════════════════════════════════════"
echo "🔍 Verifying Python imports..."
echo "════════════════════════════════════════════════════════════════"
python3 << 'EOF'
import sys

packages = {
    'numpy': 'NumPy',
    'scipy': 'SciPy',
    'transformers': 'Transformers',
    'fastapi': 'FastAPI',
    'pydantic': 'Pydantic',
    'uvicorn': 'Uvicorn',
    'click': 'Click',
    'yaml': 'PyYAML',
    'requests': 'Requests',
    'aiofiles': 'AIOFiles'
}

print("\nPackage import status:")
critical_ok = True
optional_ok = True

critical_pkgs = ['numpy', 'transformers', 'fastapi', 'pydantic', 'uvicorn']

for module, name in packages.items():
    try:
        mod = __import__(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✓ {name:20s} {version}")
    except ImportError as e:
        print(f"  ✗ {name:20s} NOT AVAILABLE ({str(e)[:40]})")
        if module in critical_pkgs:
            critical_ok = False
        else:
            optional_ok = False

print()
if critical_ok:
    print("✅ All CRITICAL packages available!")
else:
    print("❌ Some CRITICAL packages missing - app may not work")

if not optional_ok:
    print("⚠️  Some optional packages missing - some features unavailable")

# Test Pydantic version
try:
    import pydantic
    if pydantic.__version__.startswith('2.'):
        print("\n⚠️  WARNING: Pydantic v2 detected! Should be v1 for RISC-V")
        print("   Run: pip uninstall pydantic && pip install 'pydantic<2.0'")
    else:
        print(f"\n✅ Pydantic v1 ({pydantic.__version__}) - compatible with RISC-V")
except:
    pass

sys.exit(0 if critical_ok else 1)
EOF

EXIT_CODE=$?

echo ""
echo "════════════════════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ INSTALLATION SUCCESSFUL"
else
    echo "⚠️  INSTALLATION COMPLETED WITH ISSUES"
fi
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📋 Next Steps:"
echo "  1. Review log if needed: cat $LOG_FILE"
echo "  2. Test web app imports:"
echo "     python3 -c 'from src.meeting import MeetingAssistant; print(\"OK\")'"
echo "  3. Download models (if not done):"
echo "     python3 scripts/install_sbc.py --models-only"
echo "  4. Run web app:"
echo "     python3 web_app.py"
echo ""

exit $EXIT_CODE
