#!/bin/bash

# Debug script to test batch processing
SOURCE_DIR="/Volumes/SlowDisk/iCloud"
TRACKING_FILE="/Volumes/SlowDisk/iCloud/import_progress.json"
INDEX_FILE="/Volumes/SlowDisk/iCloud/folder_index.json"
BATCH_SIZE_GB=50

echo "=== Debug Batch Processing ==="
echo "Index file exists: $(test -f "$INDEX_FILE" && echo "YES" || echo "NO")"
echo "Progress file exists: $(test -f "$TRACKING_FILE" && echo "YES" || echo "NO")"

if [ -f "$INDEX_FILE" ]; then
    echo "Index summary:"
    jq '.total_folders, .total_files, .total_size_gb' "$INDEX_FILE"
fi

if [ -f "$TRACKING_FILE" ]; then
    echo "Already processed folders:"
    processed_count=$(jq '.processed_folders | length' "$TRACKING_FILE")
    echo "  Count: $processed_count"
fi

echo ""
echo "=== Testing get_folders_from_index ==="
echo "First 5 folders from index:"
jq -r '.folders[0:5][] | "\(.path)|\(.size_gb)"' "$INDEX_FILE"

echo ""
echo "=== Testing batch logic manually ==="
processed_folders=$(jq -r '.processed_folders[]' "$TRACKING_FILE" 2>/dev/null || echo "")
echo "Processed folders list: '$processed_folders'"

echo ""
echo "=== First batch candidates ==="
current_size=0
batch_count=0

jq -r '.folders[] | "\(.path)|\(.size_gb)"' "$INDEX_FILE" | while IFS='|' read -r folder folder_size_gb; do
    # Skip if already processed
    if echo "$processed_folders" | LC_ALL=C grep -Fxq "$folder"; then
        echo "SKIP (already processed): $folder"
        continue
    fi
    
    # Check if folder exists
    if [ ! -d "$folder" ]; then
        echo "SKIP (not found): $folder"
        continue
    fi
    
    # Check batch size
    would_exceed=$(awk "BEGIN {print ($current_size + $folder_size_gb > $BATCH_SIZE_GB)}")
    if [ "$would_exceed" = "1" ]; then
        echo "STOP (would exceed batch size): current=$current_size, folder=$folder_size_gb"
        break
    fi
    
    echo "INCLUDE: $folder ($folder_size_gb GB)"
    current_size=$(awk "BEGIN {printf \"%.2f\", $current_size + $folder_size_gb}")
    batch_count=$((batch_count + 1))
    
    if [ $batch_count -ge 5 ]; then
        echo "... (limiting to first 5 for testing)"
        break
    fi
done

echo ""
echo "Debug completed."