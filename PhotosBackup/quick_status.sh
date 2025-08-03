#!/bin/bash

# Quick Status Check for Large Archive Import
# Provides a concise overview of import progress

TRACKING_FILE="/Volumes/SlowDisk/iCloud/import_progress.json"
LOG_FILE="/Volumes/SlowDisk/iCloud/import_log.txt"

echo "=== Large Archive Import Status ==="

# Check if tracking file exists
if [ ! -f "$TRACKING_FILE" ]; then
    echo "❌ No import in progress"
    echo "Run: ./import_large_archive.sh to start"
    exit 0
fi

# Get basic info
STATUS=$(jq -r '.status' "$TRACKING_FILE" 2>/dev/null || echo "unknown")
BATCH=$(jq -r '.current_batch' "$TRACKING_FILE" 2>/dev/null || echo "0")
FILES=$(jq -r '.total_files_processed' "$TRACKING_FILE" 2>/dev/null || echo "0")
SIZE=$(jq -r '.total_size_processed_gb' "$TRACKING_FILE" 2>/dev/null || echo "0")
FOLDERS=$(jq -r '.processed_folders | length' "$TRACKING_FILE" 2>/dev/null || echo "0")

echo "Status: $STATUS"
echo "Batch: $BATCH"
echo "Files: $(printf "%'d" $FILES)"
echo "Size: ${SIZE} GB"
echo "Folders: $FOLDERS"

# Check if Photos app is running
if pgrep Photos > /dev/null; then
    echo "Photos: ✅ Running"
else
    echo "Photos: ❌ Not running"
fi

# Check disk space
AVAILABLE=$(df / | awk 'NR==2 {print $4}')
AVAILABLE_GB=$(echo "scale=2; $AVAILABLE * 512 / 1024 / 1024 / 1024" | bc -l)
echo "Disk Space: ${AVAILABLE_GB} GB available"

# Show last processed folder
LAST_FOLDER=$(jq -r '.last_processed_folder' "$TRACKING_FILE" 2>/dev/null)
if [ "$LAST_FOLDER" != "null" ] && [ -n "$LAST_FOLDER" ]; then
    echo "Last: $LAST_FOLDER"
fi

# Show recent log activity
if [ -f "$LOG_FILE" ]; then
    echo ""
    echo "Recent Activity:"
    tail -n 3 "$LOG_FILE" | while read -r line; do
        echo "  $line"
    done
fi

echo ""
echo "Commands:"
echo "  Status: python3 import_status.py status"
echo "  Logs:   python3 import_status.py logs"
echo "  Pause:  python3 import_status.py pause"
echo "  Resume: python3 import_status.py resume" 