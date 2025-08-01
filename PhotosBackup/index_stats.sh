#!/bin/bash

# View folder index statistics and information

set -euo pipefail

# Set locale for proper Unicode/international character handling
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SOURCE_DIR="/Volumes/SlowDisk/iCloud"
INDEX_FILE="/Volumes/SlowDisk/iCloud/folder_index.json"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Check if index file exists
if [ ! -f "$INDEX_FILE" ]; then
    warn "Index file does not exist: $INDEX_FILE"
    echo "Run ./import_large_archive.sh to create the index"
    exit 1
fi

# Check if index file is valid JSON
if ! jq -e '.created_at' "$INDEX_FILE" >/dev/null 2>&1; then
    error "Index file is corrupted or invalid format"
    exit 1
fi

echo "=== Folder Index Statistics ==="
echo ""

# Basic stats
created_at=$(jq -r '.created_at' "$INDEX_FILE")
total_folders=$(jq -r '.total_folders' "$INDEX_FILE")
total_files=$(jq -r '.total_files' "$INDEX_FILE")
total_size=$(jq -r '.total_size_gb' "$INDEX_FILE")

echo "📊 Index Information:"
echo "  Created: $created_at"
echo "  Total Folders: $total_folders"
echo "  Total Files: $total_files"
echo "  Total Size: ${total_size}GB"
echo ""

# Size distribution
echo "📁 Folder Size Distribution:"
echo "  Large folders (>1GB):"
jq -r '.folders[] | select(.size_gb > 1) | "    \(.path): \(.size_gb)GB (\(.file_count) files)"' "$INDEX_FILE" | head -10
echo ""

echo "  Folders with most files:"
jq -r '.folders[] | select(.file_count > 100) | "    \(.path): \(.file_count) files (\(.size_gb)GB)"' "$INDEX_FILE" | head -10
echo ""

# Year distribution (if folders follow date pattern)
echo "📅 Year Distribution:"
jq -r '.folders[].path' "$INDEX_FILE" | grep -E '/[0-9]{4}/' | sed -E 's|.*/([0-9]{4})/.*|\1|' | sort | uniq -c | sort -nr | head -10 | while read count year; do
    echo "  $year: $count folders"
done
echo ""

echo "💾 Index File Size: $(du -h "$INDEX_FILE" | cut -f1)"
echo ""

# Suggest actions
echo "🔧 Available Actions:"
echo "  View index file: cat $INDEX_FILE | jq ."
echo "  Force reindex: ./reindex.sh"
echo "  Start import: ./import_large_archive.sh"