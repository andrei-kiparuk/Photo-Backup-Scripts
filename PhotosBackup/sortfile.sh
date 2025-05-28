#!/bin/bash

# Define the source directory
src_dir="/Volumes/G-DRIVE/iCloudExport"

# Use find to locate all regular files in the source directory (top level only)
# -maxdepth 1 ensures we don't process files in subdirectories
# -type f selects only regular files
# -print0 separates file names with null characters to handle special characters
find "$src_dir" -maxdepth 1 -type f -print0 | while IFS= read -r -d '' file; do
    # Get the creation date using mdls, which retrieves metadata on macOS
    # -raw option outputs the date without the attribute name
    creation_date=$(mdls -name kMDItemFSCreationDate -raw "$file")

    # Check if creation_date is not empty to ensure we have a valid date
    if [ -n "$creation_date" ]; then
        # Extract the date part (YYYY-MM-DD) and convert hyphens to slashes (YYYY/MM/DD)
        date_folder=$(echo "$creation_date" | cut -d' ' -f1 | tr '-' '/')
        
        # Construct the target directory path
        target_dir="$src_dir/$date_folder"
        
        # Create the target directory (and parent directories) if it doesn't exist
        # -p prevents errors if the directory already exists
        mkdir -p "$target_dir"
        
        # Move the file to the target directory without overwriting existing files
        # -n ensures no overwrite occurs if a file with the same name exists
        mv -n "$file" "$target_dir/"
    else
        # Print a message if the creation date is missing
        echo "Skipping $file: no creation date"
    fi
done