#!/bin/bash
# Expand eMMC Partition to Use Full Disk Space

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         eMMC Storage Expansion for RISC-V                    ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Must run as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Current Storage Status"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Block devices:"
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT

echo ""
echo "Current disk usage:"
df -h /

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 Analysis"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Get partition info
TOTAL_SIZE=$(lsblk -b -d -n -o SIZE /dev/mmcblk0)
PARTITION_SIZE=$(lsblk -b -n -o SIZE /dev/mmcblk0p2)
TOTAL_GB=$(echo "scale=1; $TOTAL_SIZE / 1073741824" | bc)
PARTITION_GB=$(echo "scale=1; $PARTITION_SIZE / 1073741824" | bc)
AVAILABLE_GB=$(echo "scale=1; ($TOTAL_SIZE - $PARTITION_SIZE) / 1073741824" | bc)

echo "eMMC Total Size:     ${TOTAL_GB}G"
echo "Current Partition:   ${PARTITION_GB}G"
echo "Available to Expand: ~${AVAILABLE_GB}G"
echo ""

if (( $(echo "$AVAILABLE_GB < 1" | bc -l) )); then
    echo "ℹ️  Less than 1GB available to expand - not worth it"
    exit 0
fi

echo "⚠️  WARNING: This will expand /dev/mmcblk0p2 to use full disk"
echo ""
echo "What will happen:"
echo "  1. Expand partition /dev/mmcblk0p2 to use all available space"
echo "  2. Resize ext4 filesystem to match new partition size"
echo "  3. System will remain online during this process"
echo ""
echo "This is generally safe, but it's recommended to:"
echo "  • Have a backup of important data"
echo "  • Close all applications except this terminal"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted"
    exit 0
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Installing Required Tools"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Install cloud-utils-growpart if not available
if ! command -v growpart &> /dev/null; then
    echo "→ Installing cloud-utils-growpart..."
    apt-get update -qq
    apt-get install -y cloud-utils-growpart
else
    echo "✅ growpart already installed"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "💾 Expanding Partition"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Use growpart to expand partition (safer than manual parted)
echo "→ Expanding /dev/mmcblk0p2 to use all available space..."
if growpart /dev/mmcblk0 2; then
    echo "✅ Partition expanded successfully"
else
    # Check if already at max size
    if [ $? -eq 1 ]; then
        echo "ℹ️  Partition already at maximum size"
        # Continue anyway to resize filesystem if needed
    else
        echo "❌ Failed to expand partition"
        exit 1
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📁 Resizing Filesystem"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Resize filesystem to match new partition size
echo "→ Resizing ext4 filesystem on /dev/mmcblk0p2..."
if resize2fs /dev/mmcblk0p2; then
    echo "✅ Filesystem resized successfully"
else
    echo "⚠️  Filesystem resize had issues - checking..."
    # Try to fix filesystem first
    e2fsck -f -y /dev/mmcblk0p2 || true
    resize2fs /dev/mmcblk0p2
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ EXPANSION COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "New storage status:"
echo ""
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | grep -A2 mmcblk0
echo ""
df -h /
echo ""

# Calculate freed space
NEW_SIZE=$(df -B1 / | tail -1 | awk '{print $2}')
NEW_AVAIL=$(df -B1 / | tail -1 | awk '{print $4}')
NEW_SIZE_GB=$(echo "scale=1; $NEW_SIZE / 1073741824" | bc)
NEW_AVAIL_GB=$(echo "scale=1; $NEW_AVAIL / 1073741824" | bc)

echo "📋 Summary:"
echo "  • Partition size: ${NEW_SIZE_GB}G"
echo "  • Available space: ${NEW_AVAIL_GB}G"
echo "  • Expansion successful!"
echo ""

echo "📋 Next Steps:"
echo "  1. Verify space is available:"
echo "     df -h /"
echo ""
echo "  2. Install whisper.cpp:"
echo "     cd ~/Meetingassistant"
echo "     bash RISCV_COMPLETE_SETUP.sh"
echo ""
echo "  3. Start the app:"
echo "     source venv/bin/activate"
echo "     python3 web_app.py"
echo ""
