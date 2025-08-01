#!/bin/bash

# Force re-indexing of photo folders
# This will remove the existing index and force a full rescan on next run

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

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    error "Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

# Check if index file exists
if [ -f "$INDEX_FILE" ]; then
    log "Found existing index file: $INDEX_FILE"
    
    # Show current index stats
    if jq -e '.created_at' "$INDEX_FILE" >/dev/null 2>&1; then
        created_at=$(jq -r '.created_at' "$INDEX_FILE")
        total_folders=$(jq -r '.total_folders' "$INDEX_FILE")
        total_files=$(jq -r '.total_files' "$INDEX_FILE")
        total_size=$(jq -r '.total_size_gb' "$INDEX_FILE")
        
        echo "Current index stats:"
        echo "  Created: $created_at"
        echo "  Folders: $total_folders"
        echo "  Files: $total_files"
        echo "  Size: ${total_size}GB"
        echo ""
    fi
    
    # Ask for confirmation
    read -p "Remove existing index and force full rescan? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Reindexing cancelled."
        exit 0
    fi
    
    # Remove the index file
    rm "$INDEX_FILE"
    log "Index file removed."
else
    log "No existing index file found."
fi

log "Index will be recreated on next import run."
log "To start import: ./import_large_archive.sh"
log "To view new index stats after creation: ./index_stats.sh"