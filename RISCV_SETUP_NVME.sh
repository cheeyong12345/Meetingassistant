#!/bin/bash
# NVMe Storage Expansion for RISC-V Meeting Assistant

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         NVMe Storage Setup for RISC-V                        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Must run as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Detecting NVMe Drives"
echo "════════════════════════════════════════════════════════════════"
echo ""

# List all block devices
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT

echo ""
echo "NVMe devices:"
ls -l /dev/nvme* 2>/dev/null || echo "No NVMe devices found"

echo ""
read -p "Enter NVMe device name (e.g., nvme0n1): " NVME_DEVICE

if [ ! -b "/dev/$NVME_DEVICE" ]; then
    echo "❌ Device /dev/$NVME_DEVICE not found"
    exit 1
fi

echo ""
echo "⚠️  WARNING: This will ERASE all data on /dev/$NVME_DEVICE"
echo ""
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT /dev/$NVME_DEVICE
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted"
    exit 0
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "💾 Formatting NVMe Drive"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create partition table
echo "→ Creating GPT partition table..."
parted -s /dev/$NVME_DEVICE mklabel gpt

# Create single partition
echo "→ Creating partition..."
parted -s /dev/$NVME_DEVICE mkpart primary ext4 0% 100%

# Get partition name
if [ -b "/dev/${NVME_DEVICE}p1" ]; then
    PARTITION="/dev/${NVME_DEVICE}p1"
elif [ -b "/dev/${NVME_DEVICE}1" ]; then
    PARTITION="/dev/${NVME_DEVICE}1"
else
    echo "❌ Could not find partition"
    exit 1
fi

# Format with ext4
echo "→ Formatting with ext4..."
mkfs.ext4 -F $PARTITION

echo "✅ Drive formatted"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📁 Creating Mount Point"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Create mount point
MOUNT_POINT="/mnt/nvme"
mkdir -p $MOUNT_POINT

# Mount
echo "→ Mounting $PARTITION to $MOUNT_POINT..."
mount $PARTITION $MOUNT_POINT

# Get UUID for fstab
UUID=$(blkid -s UUID -o value $PARTITION)

# Add to fstab for auto-mount on boot
echo "→ Adding to /etc/fstab for auto-mount..."
if ! grep -q "$UUID" /etc/fstab; then
    echo "UUID=$UUID $MOUNT_POINT ext4 defaults,noatime 0 2" >> /etc/fstab
    echo "✅ Added to /etc/fstab"
else
    echo "ℹ️  Already in /etc/fstab"
fi

# Set permissions
chown -R eswin:eswin $MOUNT_POINT
chmod 755 $MOUNT_POINT

echo "✅ NVMe mounted at $MOUNT_POINT"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📦 Moving Large Directories to NVMe"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to move directory and create symlink
move_and_link() {
    local SRC=$1
    local NAME=$2
    local DEST="$MOUNT_POINT/$NAME"

    if [ -d "$SRC" ]; then
        echo "→ Moving $SRC to NVMe..."

        # Create destination
        mkdir -p "$(dirname $DEST)"

        # Copy (preserving permissions)
        rsync -av "$SRC/" "$DEST/"

        if [ $? -eq 0 ]; then
            # Backup original
            mv "$SRC" "${SRC}.old"

            # Create symlink
            ln -s "$DEST" "$SRC"

            echo "  ✅ Moved and linked: $SRC -> $DEST"
            echo "  💾 Backup at: ${SRC}.old (delete after verification)"
        else
            echo "  ❌ Failed to copy $SRC"
        fi
    else
        echo "  ℹ️  $SRC does not exist, skipping"
    fi
}

echo ""
echo "What would you like to move to NVMe?"
echo "  1. whisper.cpp models only (~1.5GB)"
echo "  2. Entire whisper.cpp directory"
echo "  3. pip cache and build directories"
echo "  4. All of the above (recommended)"
echo "  5. Custom selection"
echo ""
read -p "Choose [1-5]: " CHOICE

case $CHOICE in
    1)
        move_and_link "/home/eswin/whisper.cpp/models" "whisper-models"
        ;;
    2)
        move_and_link "/home/eswin/whisper.cpp" "whisper.cpp"
        ;;
    3)
        move_and_link "/home/eswin/.cache/pip" "cache/pip"
        move_and_link "/tmp/pip-ephem-wheel-cache" "cache/pip-wheels"
        ;;
    4)
        echo "Moving all recommended directories..."
        move_and_link "/home/eswin/whisper.cpp" "whisper.cpp"
        move_and_link "/home/eswin/.cache" "cache"

        # Create directories for future use
        mkdir -p $MOUNT_POINT/models
        mkdir -p $MOUNT_POINT/data
        chown -R eswin:eswin $MOUNT_POINT/models
        chown -R eswin:eswin $MOUNT_POINT/data

        echo "  ✅ Created: $MOUNT_POINT/models (for future models)"
        echo "  ✅ Created: $MOUNT_POINT/data (for meeting recordings)"
        ;;
    5)
        echo ""
        echo "Custom directories to move (one per line, empty to finish):"
        while true; do
            read -p "Source path: " SRC_PATH
            if [ -z "$SRC_PATH" ]; then
                break
            fi
            read -p "Name on NVMe: " DEST_NAME
            move_and_link "$SRC_PATH" "$DEST_NAME"
        done
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 Storage Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Before:"
echo "  Root partition: 27G used / 28G total (99%)"
echo ""
echo "After:"
df -h / | tail -1 | awk '{print "  Root partition: " $3 " used / " $2 " total (" $5 ")"}'
df -h $MOUNT_POINT | tail -1 | awk '{print "  NVMe storage:   " $3 " used / " $2 " total (" $5 ")"}'

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ NVMe SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Summary:"
echo "  • NVMe device: /dev/$NVME_DEVICE"
echo "  • Partition: $PARTITION"
echo "  • Mount point: $MOUNT_POINT"
echo "  • UUID: $UUID"
echo "  • Auto-mount: Enabled (via /etc/fstab)"
echo ""
echo "📋 What Was Moved:"
ls -la $MOUNT_POINT/
echo ""
echo "📋 Cleanup (After Verification):"
echo "  # Delete old backups to free space:"
find /home/eswin -name "*.old" -type d 2>/dev/null | while read dir; do
    echo "  sudo rm -rf '$dir'"
done
echo ""
echo "📋 Next Steps:"
echo "  1. Verify everything works:"
echo "     cd ~/Meetingassistant"
echo "     source venv/bin/activate"
echo "     bash RISCV_COMPLETE_SETUP.sh"
echo ""
echo "  2. Delete .old backups to free space:"
echo "     sudo rm -rf /home/eswin/whisper.cpp.old"
echo "     sudo rm -rf /home/eswin/.cache.old"
echo ""
echo "  3. Start the app:"
echo "     python3 web_app.py"
echo ""
echo "💡 Tips:"
echo "  • NVMe auto-mounts on boot"
echo "  • Symlinks make it transparent"
echo "  • You can store models/data on NVMe"
echo "  • To manually mount: sudo mount -a"
echo ""
