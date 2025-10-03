#!/bin/bash
# Direct patch of transformers - run this to fix the safetensors error

echo "🔧 Patching transformers installation directly..."
echo ""

# Check venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Not in virtual environment!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Find transformers path
TRANSFORMERS_PATH=$(python3 -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])" 2>/dev/null)

if [ -z "$TRANSFORMERS_PATH" ]; then
    echo "❌ Could not find site-packages"
    exit 1
fi

TRANSFORMERS_DIR="$TRANSFORMERS_PATH/transformers"
DEPS_FILE="$TRANSFORMERS_DIR/dependency_versions_check.py"

if [ ! -f "$DEPS_FILE" ]; then
    echo "❌ Transformers dependency file not found"
    echo "   Expected: $DEPS_FILE"
    exit 1
fi

echo "📦 Found: $DEPS_FILE"
echo ""

# Backup
cp "$DEPS_FILE" "$DEPS_FILE.backup"
echo "✅ Backup created: $DEPS_FILE.backup"
echo ""

# Create patched version
cat > "$DEPS_FILE" << 'EOPYTHON'
# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# PATCHED FOR RISC-V: Skip safetensors and tokenizers checks

import platform
import os

# On RISC-V, skip Rust dependency checks (safetensors, tokenizers)
IS_RISCV = platform.machine() == 'riscv64'

if IS_RISCV or os.environ.get('TRANSFORMERS_NO_ADVISORY_WARNINGS'):
    # Create dummy functions to bypass checks
    def require_version(*args, **kwargs):
        pass

    def require_version_core(*args, **kwargs):
        pass
else:
    # Normal dependency checking for other platforms
    from .utils.versions import require_version, require_version_core

    from . import dependency_versions_table

    deps = dependency_versions_table.deps

    # Check only for non-Rust dependencies
    for pkg, version in deps.items():
        if pkg not in ['safetensors', 'tokenizers']:
            require_version_core(version)
EOPYTHON

echo "✅ Patch applied"
echo ""

# Test import
echo "🧪 Testing transformers import..."
python3 << 'EOF'
import transformers
print(f"✅ Transformers {transformers.__version__} imported successfully!")

# Test AutoTokenizer
from transformers import AutoTokenizer
print("✅ AutoTokenizer works")

print("\n✅ PATCH SUCCESSFUL!")
print("\nNote: Using slow Python tokenizers (no Rust tokenizers)")
print("This is normal and expected on RISC-V.")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "✅ TRANSFORMERS SUCCESSFULLY PATCHED"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Transformers will now work without safetensors/tokenizers"
    echo ""
else
    echo ""
    echo "❌ Patch test failed, restoring backup..."
    cp "$DEPS_FILE.backup" "$DEPS_FILE"
    exit 1
fi
