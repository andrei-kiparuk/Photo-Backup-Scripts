#!/bin/bash

# Large Archive Import Script
# Handles 8TB+ of photos with batch processing, duplicate detection, and resumability

set -euo pipefail

# Ensure Homebrew bc is available (needed for floating point calculations)
export PATH="/opt/homebrew/opt/bc/bin:$PATH"

# Configuration
SOURCE_DIR="/Volumes/SlowDisk/iCloud"
TRACKING_FILE="/Volumes/SlowDisk/iCloud/import_progress.json"
LOG_FILE="/Volumes/SlowDisk/iCloud/import_log.txt"
BATCH_SIZE_GB=50
ALBUM_NAME="import2025"
MAX_RETRIES=3
PHOTOS_RESTART_THRESHOLD=1000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

# Check dependencies
check_dependencies() {
    local missing=()
    
    # Check system dependencies
    local system_deps=("exiftool" "python3" "jq" "bc")
    for dep in "${system_deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
    
    # Check Python packages (must be in virtual environment)
    if ! python -c "import osxphotos" &> /dev/null 2>&1; then
        missing+=("python package: osxphotos")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        error "Make sure you're in the virtual environment: source ./venv/bin/activate"
        error "If dependencies are missing, run: ./setup_import.sh"
        exit 1
    fi
    
    log "All dependencies are available"
}

# Initialize or load progress tracking
init_progress() {
    if [ ! -f "$TRACKING_FILE" ]; then
        log "Creating new progress tracking file"
        cat > "$TRACKING_FILE" << EOF
{
    "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "total_files_processed": 0,
    "total_size_processed_gb": 0,
    "current_batch": 1,
    "processed_folders": [],
    "failed_files": [],
    "duplicate_files": [],
    "last_processed_folder": null,
    "status": "running"
}
EOF
    else
        log "Loading existing progress from $TRACKING_FILE"
    fi
}

# Update progress tracking
update_progress() {
    local folder="$1"
    local files_processed="$2"
    local size_gb="$3"
    
    # Create temporary file for atomic update
    local temp_file=$(mktemp)
    
    jq --arg folder "$folder" \
       --argjson files "$files_processed" \
       --argjson size "$size_gb" \
       --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.processed_folders += [$folder] |
        .total_files_processed += $files |
        .total_size_processed_gb += $size |
        .last_processed_folder = $folder |
        .last_update = $timestamp' "$TRACKING_FILE" > "$temp_file"
    
    mv "$temp_file" "$TRACKING_FILE"
}

# Get next batch of folders to process
get_next_batch() {
    local current_size=0
    local batch_folders=()
    local processed_folders
    
    # Get list of already processed folders
    processed_folders=$(jq -r '.processed_folders[]' "$TRACKING_FILE" 2>/dev/null || echo "")
    
    # Find all YYYY/MM/DD folders in chronological order
    find "$SOURCE_DIR" -type d -regex '.*/[0-9]\{4\}/[0-9]\{2\}/[0-9]\{2\}$' | sort | while read -r folder; do
        # Skip if already processed
        if echo "$processed_folders" | grep -q "^$folder$"; then
            continue
        fi
        
        # Calculate folder size
        local folder_size=$(du -sb "$folder" 2>/dev/null | cut -f1)
        local folder_size_gb=$(echo "scale=2; $folder_size / 1024 / 1024 / 1024" | bc -l)
        
        # Check if adding this folder would exceed batch size
        if (( $(echo "$current_size + $folder_size_gb > $BATCH_SIZE_GB" | bc -l) )); then
            break
        fi
        
        batch_folders+=("$folder")
        current_size=$(echo "$current_size + $folder_size_gb" | bc -l)
        
        # Output folder info for processing
        echo "$folder|$folder_size_gb"
    done
}

# Process a single folder
process_folder() {
    local folder="$1"
    local temp_dir="/tmp/import_batch_$$"
    
    log "Processing folder: $folder"
    
    # Create temporary directory for this batch
    mkdir -p "$temp_dir"
    
    # Copy files to temp directory with proper date handling
    python3 -c "
import sys
sys.path.append('.')
from date_fixer import fix_file_dates_in_folder
fix_file_dates_in_folder('$folder', '$temp_dir')
"
    
    # Import to Photos with duplicate detection
    local import_result=0
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        log "Importing batch (attempt $((retry_count + 1)))"
        
        if osxphotos import "$temp_dir" \
            --parse-folder-date "%Y/%m/%d" \
            --sidecar \
            --exiftool \
            --skip-dups \
            --resume \
            --walk \
            --verbose \
            --album "$ALBUM_NAME" \
            --stop-on-error 5 2>&1 | tee -a "$LOG_FILE"; then
            import_result=0
            break
        else
            import_result=$?
            retry_count=$((retry_count + 1))
            
            if [ $retry_count -lt $MAX_RETRIES ]; then
                warn "Import failed, restarting Photos app and retrying..."
                restart_photos_app
                sleep 10
            fi
        fi
    done
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    if [ $import_result -eq 0 ]; then
        log "Successfully imported folder: $folder"
        return 0
    else
        error "Failed to import folder: $folder after $MAX_RETRIES attempts"
        return 1
    fi
}

# Restart Photos app
restart_photos_app() {
    log "Restarting Photos app..."
    
    # Force quit Photos
    osascript -e 'tell application "Photos" to quit' 2>/dev/null || true
    sleep 5
    
    # Force kill if still running
    if pgrep Photos > /dev/null; then
        killall -9 Photos 2>/dev/null || true
        sleep 5
    fi
    
    # Start Photos
    open -a Photos
    sleep 15
    
    log "Photos app restarted"
}

# Check available disk space
check_disk_space() {
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local available_gb=$(echo "scale=2; $available_space * 512 / 1024 / 1024 / 1024" | bc -l)
    
    if (( $(echo "$available_gb < 10" | bc -l) )); then
        error "Low disk space: ${available_gb}GB available. Need at least 10GB for processing."
        return 1
    fi
    
    log "Available disk space: ${available_gb}GB"
    return 0
}

# Main processing loop
main() {
    log "Starting large archive import process"
    log "Source: $SOURCE_DIR"
    log "Batch size: ${BATCH_SIZE_GB}GB"
    log "Album: $ALBUM_NAME"
    
    # Check dependencies
    check_dependencies
    
    # Check source directory exists
    if [ ! -d "$SOURCE_DIR" ]; then
        error "Source directory does not exist: $SOURCE_DIR"
        exit 1
    fi
    
    # Initialize progress tracking
    init_progress
    
    # Main processing loop
    while true; do
        # Check disk space
        if ! check_disk_space; then
            error "Insufficient disk space. Stopping import process."
            break
        fi
        
        # Get next batch
        local batch_info
        batch_info=$(get_next_batch)
        
        if [ -z "$batch_info" ]; then
            log "No more folders to process. Import complete!"
            break
        fi
        
        # Process each folder in the batch
        local total_files=0
        local total_size=0
        
        while IFS='|' read -r folder size_gb; do
            if [ -n "$folder" ]; then
                if process_folder "$folder"; then
                    total_files=$((total_files + $(find "$folder" -type f | wc -l)))
                    total_size=$(echo "$total_size + $size_gb" | bc -l)
                else
                    warn "Failed to process folder: $folder"
                fi
            fi
        done <<< "$batch_info"
        
        # Update progress
        update_progress "" "$total_files" "$total_size"
        
        # Restart Photos app periodically
        local current_batch=$(jq -r '.current_batch' "$TRACKING_FILE")
        if [ "$((current_batch % 5))" -eq 0 ]; then
            log "Restarting Photos app after batch $current_batch"
            restart_photos_app
        fi
        
        # Update batch counter
        jq --argjson batch $((current_batch + 1)) '.current_batch = $batch' "$TRACKING_FILE" > "${TRACKING_FILE}.tmp" && mv "${TRACKING_FILE}.tmp" "$TRACKING_FILE"
        
        log "Completed batch $current_batch. Processed $total_files files, ${total_size}GB"
    done
    
    log "Import process completed successfully!"
}

# Handle script interruption
cleanup() {
    log "Script interrupted. Saving progress..."
    jq '.status = "interrupted" | .last_update = "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"' "$TRACKING_FILE" > "${TRACKING_FILE}.tmp" && mv "${TRACKING_FILE}.tmp" "$TRACKING_FILE"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@" 