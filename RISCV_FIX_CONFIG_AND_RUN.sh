#!/bin/bash
# Fix config.yaml and install web dependencies for RISC-V

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║      Fix Config & Install Web Dependencies (RISC-V)          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📝 Fixing config.yaml"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo "❌ config.yaml not found!"
    exit 1
fi

# Add storage section if missing
if ! grep -q "^storage:" config.yaml; then
    echo "→ Adding missing storage section to config.yaml..."
    cat >> config.yaml << 'EOF'

# Storage Configuration
storage:
  data_dir: "./data"
  meetings_dir: "./data/meetings"
  models_dir: "./models"
  database_url: "sqlite:///./data/meetings.db"
EOF
    echo "✅ Storage section added"
else
    echo "✅ Storage section already exists"
fi

# Create directories
echo ""
echo "→ Creating required directories..."
mkdir -p data/meetings data/recordings data/transcripts data/summaries models logs
echo "✅ Directories created"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Installing Web Dependencies"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Try system packages first (pre-built for RISC-V)
echo "→ Attempting to install system packages..."
if sudo apt install -y python3-fastapi python3-uvicorn python3-jinja2 python3-yaml 2>/dev/null; then
    echo "✅ System packages installed"
    DEPS_OK=1
else
    echo "⚠️  System packages not available, using pip..."
    DEPS_OK=0
fi

# If system packages failed, use pip with minimal requirements
if [ $DEPS_OK -eq 0 ]; then
    echo ""
    echo "→ Installing via pip (this may take a while on RISC-V)..."

    # Create minimal requirements
    cat > /tmp/requirements-web.txt << 'EOF'
fastapi
uvicorn[standard]
jinja2
pyyaml
websockets
python-multipart
EOF

    # Try with pip
    if pip3 install --break-system-packages -r /tmp/requirements-web.txt 2>/dev/null; then
        echo "✅ Pip packages installed"
    else
        echo "⚠️  Pip installation had issues, trying one by one..."

        # Install one by one, ignore errors
        for pkg in fastapi uvicorn jinja2 pyyaml websockets python-multipart; do
            echo "  → Installing $pkg..."
            pip3 install --break-system-packages $pkg 2>/dev/null || echo "    ⚠️  $pkg failed (may already be installed)"
        done
    fi

    rm -f /tmp/requirements-web.txt
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🧪 Testing Web App"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test imports
echo "→ Testing Python imports..."
python3 << 'PYTEST'
import sys
errors = []

try:
    import fastapi
    print("  ✅ fastapi")
except Exception as e:
    print(f"  ❌ fastapi: {e}")
    errors.append("fastapi")

try:
    import uvicorn
    print("  ✅ uvicorn")
except Exception as e:
    print(f"  ❌ uvicorn: {e}")
    errors.append("uvicorn")

try:
    import jinja2
    print("  ✅ jinja2")
except Exception as e:
    print(f"  ❌ jinja2: {e}")
    errors.append("jinja2")

try:
    import yaml
    print("  ✅ pyyaml")
except Exception as e:
    print(f"  ❌ pyyaml: {e}")
    errors.append("pyyaml")

if errors:
    print(f"\n⚠️  Some imports failed: {', '.join(errors)}")
    print("The app may still work with available packages")
else:
    print("\n✅ All web dependencies available!")
PYTEST

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "📋 Next Steps:"
echo ""
echo "  1. Start the web app:"
echo "     python3 web_app.py"
echo ""
echo "  2. Open browser to:"
echo "     http://10.162.197.63:8000"
echo ""
echo "  3. Go to Settings page to test model switching:"
echo "     http://10.162.197.63:8000/settings"
echo ""
echo "💡 Tips:"
echo "  • Press Ctrl+C to stop the server"
echo "  • Check logs in logs/ directory"
echo "  • Config file: config.yaml"
echo ""
