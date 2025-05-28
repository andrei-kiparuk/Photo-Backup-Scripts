#!/bin/bash

# Define directory paths
SOURCE_DIR="/Volumes/G-DRIVE/Converted"
FAILED_DIR="/Volumes/G-DRIVE/Failed"
TEMP_DIR="$HOME/Downloads/tmp"

# Create Failed and Temp directories if they don't exist
mkdir -p "$FAILED_DIR"
mkdir -p "$TEMP_DIR"

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

# Find all media files with common photo and video extensions (case-insensitive)
find "$SOURCE_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.bmp" -o -iname "*.tiff" -o -iname "*.heic" -o -iname "*.mov" -o -iname "*.mp4" -o -iname "*.m4v" -o -iname "*.avi" \) | sort -r | while read -r file; do
    # Check available space on the drive containing the home folder (in MB)
    avail_mb=$(df -m ~ | tail -1 | awk '{print $4}')
    threshold_mb=$((120 * 1024)) # 120GB in MB
    if [ "$avail_mb" -lt "$threshold_mb" ]; then
        echo "Available space is less than 120GB. Exiting script."
        exit 1
    fi

    # Calculate the relative path by removing the source directory prefix
    relative_path="${file#${SOURCE_DIR}/}"
    
    # Construct temporary file path preserving the original file name and subfolder structure
    temp_file="$TEMP_DIR/$relative_path"
    
    # Create the target directory structure in the temporary folder if it doesn't exist
    mkdir -p "$(dirname "$temp_file")"
    
    # Copy the original file to the temporary location
    cp "$file" "$temp_file"
    
    echo "Processing $file (copied to $temp_file)"
    
    # Attempt to import the temporary file into Photos using AppleScript
    result=$(osascript <<EOF
tell application "Photos"
    try
        import POSIX file "$temp_file" skip check duplicates true
        return "success"
    on error
        return "failure"
    end try
end tell
EOF
)
    
    # Handle the original file based on import result
    if [ "$result" == "success" ]; then
        # Delete the original file after successful import
        rm "$file"
        echo "Successfully imported and deleted $file"
    else
        # Construct target failed path preserving subfolder structure
        target_failed="$FAILED_DIR/$relative_path"
        # Create the target directory structure if it doesn't exist
        mkdir -p "$(dirname "$target_failed")"
        # Move the original file to Failed directory
        mv "$file" "$target_failed"
        echo "Failed to import $file, moved to $target_failed"
    fi
    
    # Remove the temporary file after import attempt
    rm "$temp_file"
done