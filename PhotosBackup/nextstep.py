import os
import shutil
from datetime import datetime

# Configuration
source_base_path = "/Volumes/RAID/unpack/Takeout/Google Photos"
destination_base_path = "/Volumes/RAID/NextStep"
date_threshold = datetime(2024, 11, 16)

# Function to ensure the destination folder exists
def ensure_destination_path(destination_path):
    os.makedirs(destination_path, exist_ok=True)

# Function to check if a file was created after the threshold
def is_created_after_threshold(file_path):
    try:
        stat = os.stat(file_path)
        file_creation_date = datetime.fromtimestamp(stat.st_mtime)  # Modification time
        return file_creation_date > date_threshold
    except Exception as e:
        print(f"Error checking date for {file_path}: {e}")
        return False

# Function to move a file while preserving folder structure
def move_file_with_structure(source_file_path, source_base, destination_base):
    try:
        relative_path = os.path.relpath(source_file_path, source_base)
        destination_file_path = os.path.join(destination_base, relative_path)
        
        # Ensure the destination directory exists
        destination_dir = os.path.dirname(destination_file_path)
        ensure_destination_path(destination_dir)
        
        # Move the file
        shutil.move(source_file_path, destination_file_path)
        print(f"Moved: {source_file_path} -> {destination_file_path}")
    except Exception as e:
        print(f"Failed to move {source_file_path}: {e}")

# Function to process the source directory
def process_source_directory(source_base, destination_base):
    for root, _, files in os.walk(source_base):
        for file_name in files:
            source_file_path = os.path.join(root, file_name)
            
            # Check if the file was created after the threshold
            if is_created_after_threshold(source_file_path):
                move_file_with_structure(source_file_path, source_base, destination_base)

# Run the script
print(f"Processing files in {source_base_path}...")
process_source_directory(source_base_path, destination_base_path)
print("Processing complete.")
