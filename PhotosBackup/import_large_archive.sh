#!/bin/bash

# Large Archive Import Script
# Handles 8TB+ of photos with batch processing, duplicate detection, and resumability

set -euo pipefail

# Set locale for proper Unicode/international character handling
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Configuration
SOURCE_DIR="/Volumes/SlowDisk/iCloud"
TRACKING_FILE="/Volumes/SlowDisk/iCloud/import_progress.json"
LOG_FILE="/Volumes/SlowDisk/iCloud/import_log.txt"
INDEX_FILE="/Volumes/SlowDisk/iCloud/folder_index.json"
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
    local system_deps=("exiftool" "python3" "jq" "awk")
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

# Create or update folder index
create_folder_index() {
    log "Creating folder index... This may take a few minutes on first run."
    
    local temp_index=$(mktemp)
    cat > "$temp_index" << 'EOF'
{
    "created_at": "",
    "total_folders": 0,
    "total_files": 0,
    "total_size_gb": 0,
    "folders": []
}
EOF

    local folder_count=0
    local total_files=0
    local total_size=0
    
    # Get creation timestamp
    jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '.created_at = $timestamp' "$temp_index" > "${temp_index}.tmp" && mv "${temp_index}.tmp" "$temp_index"
    
    log "Scanning directories for media files..."
    
    # Find all folders that contain image/video files
    while read -r folder; do
        # Skip the root source directory itself
        if [ "$folder" = "$SOURCE_DIR" ]; then
            continue
        fi
        
        # Check if folder contains any image/video files (recursive search, Unicode-safe)
        local has_media_files=$(find "$folder" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.webp" -o -iname "*.heic" -o -iname "*.mov" -o -iname "*.mp4" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.m4v" -o -iname "*.wmv" -o -iname "*.flv" -o -iname "*.3gp" \) -print -quit 2>/dev/null)
        if [ -z "$has_media_files" ]; then
            continue
        fi
        
        # Calculate folder size and file count (using macOS-compatible du command)
        local folder_size_kb=$(du -sk "$folder" 2>/dev/null | cut -f1)
        local file_count=$(find "$folder" -type f | wc -l)
        
        # Validate folder size is numeric
        if [[ ! "$folder_size_kb" =~ ^[0-9]+$ ]] || [ -z "$folder_size_kb" ]; then
            echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} Could not determine size for folder: $folder" >> "$LOG_FILE"
            continue
        fi
        
        # Calculate size in GB (convert from KB to GB)
        local folder_size_gb=$(awk "BEGIN {printf \"%.2f\", $folder_size_kb / 1024 / 1024}")
        
        # Add folder to index
        jq --arg path "$folder" \
           --arg size_gb "$folder_size_gb" \
           --argjson file_count "$file_count" \
           '.folders += [{"path": $path, "size_gb": ($size_gb | tonumber), "file_count": $file_count}]' \
           "$temp_index" > "${temp_index}.tmp" && mv "${temp_index}.tmp" "$temp_index"
        
        folder_count=$((folder_count + 1))
        total_files=$((total_files + file_count))
        total_size=$(awk "BEGIN {printf \"%.2f\", $total_size + $folder_size_gb}")
        
        # Show progress every 100 folders
        if [ $((folder_count % 100)) -eq 0 ]; then
            log "Indexed $folder_count folders so far..."
        fi
    done < <(find "$SOURCE_DIR" -type d | sort)
    
    # Update summary statistics (ensure total_size is a valid number)
    if [ -z "$total_size" ] || [ "$total_size" = "" ]; then
        total_size="0.00"
    fi
    
    jq --argjson total_folders "$folder_count" \
       --argjson total_files "$total_files" \
       --arg total_size "$total_size" \
       '.total_folders = $total_folders | .total_files = $total_files | .total_size_gb = ($total_size | tonumber)' \
       "$temp_index" > "${temp_index}.tmp" && mv "${temp_index}.tmp" "$temp_index"
    
    # Move to final location
    mv "$temp_index" "$INDEX_FILE"
    
    log "Folder index created: $folder_count folders, $total_files files, ${total_size}GB"
}

# Check if index file exists and is valid
check_index_validity() {
    if [ ! -f "$INDEX_FILE" ]; then
        return 1  # Index doesn't exist
    fi
    
    # Check if index file is valid JSON and has required structure
    if ! jq -e '.created_at and .folders and (.folders | type == "array")' "$INDEX_FILE" >/dev/null 2>&1; then
        warn "Index file is corrupted or invalid format"
        return 1
    fi
    
    # Check if source directory still exists
    if [ ! -d "$SOURCE_DIR" ]; then
        warn "Source directory no longer exists"
        return 1
    fi
    
    return 0  # Index is valid
}

# Get folder information from index
get_folders_from_index() {
    if ! check_index_validity; then
        log "Index file missing or invalid, creating new index..."
        create_folder_index
    fi
    
    local index_created=$(jq -r '.created_at' "$INDEX_FILE")
    local total_folders=$(jq -r '.total_folders' "$INDEX_FILE")
    local total_files=$(jq -r '.total_files' "$INDEX_FILE")
    local total_size=$(jq -r '.total_size_gb' "$INDEX_FILE")
    
    log "Using folder index (created: $index_created)"
    log "Index contains: $total_folders folders, $total_files files, ${total_size}GB"
    
    # Extract folder paths and sizes
    jq -r '.folders[] | "\(.path)|\(.size_gb)"' "$INDEX_FILE"
}

# Get next batch of folders to process
get_next_batch() {
    local current_size=0
    local batch_folders=()
    local processed_folders
    
    # Get list of already processed folders
    processed_folders=$(jq -r '.processed_folders[]' "$TRACKING_FILE" 2>/dev/null || echo "")
    
    # Get all folders from index (creates index if needed)
    get_folders_from_index | while IFS='|' read -r folder folder_size_gb; do
        # Skip if already processed (Unicode-safe)
        if echo "$processed_folders" | LC_ALL=C grep -Fxq "$folder"; then
            continue
        fi
        
        # Validate folder still exists
        if [ ! -d "$folder" ]; then
            echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} Folder no longer exists: $folder" >> "$LOG_FILE"
            continue
        fi
        
        # Check if adding this folder would exceed batch size
        local would_exceed=$(awk "BEGIN {print ($current_size + $folder_size_gb > $BATCH_SIZE_GB)}")
        if [ "$would_exceed" = "1" ]; then
            break
        fi
        
        batch_folders+=("$folder")
        current_size=$(awk "BEGIN {printf \"%.2f\", $current_size + $folder_size_gb}")
        
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
    
    # Validate available_space is numeric
    if [[ ! "$available_space" =~ ^[0-9]+$ ]] || [ -z "$available_space" ]; then
        warn "Could not determine available disk space"
        return 0  # Continue processing if we can't check
    fi
    
    # Calculate available GB using awk
    local available_gb=$(awk "BEGIN {printf \"%.2f\", $available_space * 512 / 1024 / 1024 / 1024}")
    
    # Check if less than 10GB available
    local low_space=$(awk "BEGIN {print ($available_gb < 10)}")
    if [ "$low_space" = "1" ]; then
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
            # Validate folder path looks legitimate and exists
            if [ -n "$folder" ] && [[ "$folder" =~ ^/.* ]] && [ -d "$folder" ]; then
                if process_folder "$folder"; then
                    total_files=$((total_files + $(find "$folder" -type f | wc -l)))
                    total_size=$(awk "BEGIN {printf \"%.2f\", $total_size + $size_gb}")
                else
                    warn "Failed to process folder: $folder"
                fi
            elif [ -n "$folder" ]; then
                # Log invalid folder path to file only
                echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} Skipping invalid folder path: $folder" >> "$LOG_FILE"
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