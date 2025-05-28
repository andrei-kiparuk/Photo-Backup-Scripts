#!/bin/bash

# Check if source and destination directories are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_directory> <destination_directory>"
    exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="$2"
LOG_FILE="${DEST_DIR}/move_long_videos_$(date +%F_%H-%M-%S).log"

# Check if ffprobe is installed
if ! command -v ffprobe &> /dev/null; then
    echo "Error: ffprobe (part of ffmpeg) is not installed. Please install ffmpeg."
    exit 1
fi

# Resolve absolute path for source directory
if ! SOURCE_DIR=$(realpath "$SOURCE_DIR" 2>/dev/null); then
    echo "Error: Source directory does not exist or is invalid: $1"
    exit 1
fi

# Check if source directory is readable
if [ ! -r "$SOURCE_DIR" ]; then
    echo "Error: Source directory is not readable: $SOURCE_DIR"
    exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    if ! mkdir -p "$DEST_DIR" 2>/dev/null; then
        echo "Error: Failed to create destination directory: $DEST_DIR"
        exit 1
    fi
fi

# Resolve absolute path for destination directory
if ! DEST_DIR=$(realpath "$DEST_DIR" 2>/dev/null); then
    echo "Error: Cannot resolve destination directory after creation: $2"
    exit 1
fi

# Check if destination directory is writable
if [ ! -w "$DEST_DIR" ]; then
    echo "Error: No write permission for destination directory: $DEST_DIR"
    exit 1
fi

# Initialize log file
echo "Move Long Videos Log - Started at $(date)" > "$LOG_FILE"
echo "Source: $SOURCE_DIR" >> "$LOG_FILE"
echo "Destination: $DEST_DIR" >> "$LOG_FILE"
echo "----------------------------------------" >> "$LOG_FILE"

# Function to process each video file
process_video() {
    local file="$1"
    local relative_path="${file#$SOURCE_DIR/}"
    local dest_path="$DEST_DIR/$relative_path"
    local dest_dir=$(dirname "$dest_path")

    # Check if file exists
    if [ ! -f "$file" ]; then
        echo "Error: File does not exist: $file" | tee -a "$LOG_FILE"
        return
    fi

    # Get video duration in seconds using ffprobe
    duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$file" 2>/dev/null)

    # Check if duration is a valid number and greater than 10 minutes (600 seconds)
    if [[ -z "$duration" ]]; then
        echo "Warning: Could not determine duration for $relative_path" | tee -a "$LOG_FILE"
        return
    fi

    if [[ $(echo "$duration > 70" | bc -l) -eq 1 ]]; then
        # Create destination directory structure
        if ! mkdir -p "$dest_dir" 2>>"$LOG_FILE"; then
            echo "Error: Failed to create directory $dest_dir" | tee -a "$LOG_FILE"
            return
        fi

        # Move the file
        if mv -f "$file" "$dest_path" 2>>"$LOG_FILE"; then
            echo "Moved: $relative_path -> $dest_path" | tee -a "$LOG_FILE"
        else
            echo "Error: Failed to move $relative_path to $dest_path" | tee -a "$LOG_FILE"
        fi
    fi
}

# Export the function for use with find
export -f process_video
export SOURCE_DIR DEST_DIR LOG_FILE

# Find all video files and process them
find "$SOURCE_DIR" -type f \( -iname "*.mp4" -o -iname "*.mov" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.wmv" \) -exec bash -c 'process_video "$0"' {} \;

echo "Processing complete! Check log file for details: $LOG_FILE" | tee -a "$LOG_FILE"