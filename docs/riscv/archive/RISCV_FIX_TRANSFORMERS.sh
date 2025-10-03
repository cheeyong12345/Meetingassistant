#!/bin/bash
# Permanently patch transformers to skip safetensors/tokenizers checks on RISC-V

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║    Patch Transformers for RISC-V (Skip Safetensors Check)   ║"
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

# Find transformers installation
TRANSFORMERS_PATH=$(python3 -c "import transformers; import os; print(os.path.dirname(transformers.__file__))" 2>/dev/null)

if [ -z "$TRANSFORMERS_PATH" ]; then
    echo "❌ Transformers not installed"
    exit 1
fi

echo "📦 Transformers path: $TRANSFORMERS_PATH"
echo ""

# Backup original file
DEPS_FILE="$TRANSFORMERS_PATH/dependency_versions_check.py"

if [ ! -f "$DEPS_FILE" ]; then
    echo "❌ File not found: $DEPS_FILE"
    exit 1
fi

echo "📝 Backing up original file..."
cp "$DEPS_FILE" "$DEPS_FILE.backup"
echo "   ✅ Backup: $DEPS_FILE.backup"
echo ""

# Patch the file
echo "🔧 Patching dependency check..."

python3 << 'EOF'
import sys
import os

# Find transformers path
import transformers
transformers_path = os.path.dirname(transformers.__file__)
deps_file = os.path.join(transformers_path, "dependency_versions_check.py")

print(f"Patching: {deps_file}")

# Read original
with open(deps_file, 'r') as f:
    content = f.read()

# Add RISC-V patch at the beginning
patch = '''# RISC-V Patch: Skip safetensors and tokenizers checks (not available on RISC-V)
import platform
import os

if platform.machine() == 'riscv64' or os.environ.get('TRANSFORMERS_NO_ADVISORY_WARNINGS'):
    # Monkey-patch require_version to skip Rust dependencies
    from transformers.utils import versions
    _original_require = versions.require_version

    def _patched_require(requirement, hint=None):
        # Skip safetensors and tokenizers on RISC-V
        if 'safetensors' in requirement or 'tokenizers' in requirement:
            return
        return _original_require(requirement, hint)

    versions.require_version = _patched_require

'''

# Insert patch after imports
import_end = content.find('\n\n')
if import_end > 0:
    new_content = content[:import_end] + '\n\n' + patch + content[import_end:]
else:
    new_content = patch + '\n' + content

# Write patched version
with open(deps_file, 'w') as f:
    f.write(new_content)

print("✅ Patch applied successfully")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Patch failed, restoring backup..."
    cp "$DEPS_FILE.backup" "$DEPS_FILE"
    exit 1
fi

echo ""
echo "🧪 Testing patched transformers..."
python3 << 'EOF'
import transformers
print(f"✅ Transformers {transformers.__version__} loads without errors")

from transformers import AutoTokenizer
print("✅ AutoTokenizer works")

print("\n✅ Patch successful!")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Test failed, restoring backup..."
    cp "$DEPS_FILE.backup" "$DEPS_FILE"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ TRANSFORMERS PATCHED SUCCESSFULLY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "The patch:"
echo "  • Automatically detects RISC-V architecture"
echo "  • Skips safetensors and tokenizers version checks"
echo "  • Uses slow Python tokenizers instead (works fine)"
echo ""
echo "Backup saved at:"
echo "  $DEPS_FILE.backup"
echo ""
echo "To restore original:"
echo "  cp $DEPS_FILE.backup $DEPS_FILE"
echo ""
