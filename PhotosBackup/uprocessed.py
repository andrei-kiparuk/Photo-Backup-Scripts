import os
import json
import shutil
from datetime import datetime

# Configuration
base_path = "/Volumes/G-DRIVE/unpack/Takeout/Google Photos"
unproceed_path = "/Volumes/G-DRIVE/unpack/Takeout/unproceed"
failed_log_path = "failed_files.log"
date_threshold = datetime(2024, 11, 17)

# Ensure the unproceed folder exists
os.makedirs(unproceed_path, exist_ok=True)

# Function to move a file to the unproceed folder
def move_to_unproceed(file_path):
    try:
        if os.path.exists(file_path):
            dest_path = os.path.join(unproceed_path, os.path.basename(file_path))
            shutil.move(file_path, dest_path)
            print(f"Moved to unproceed: {file_path}")
    except Exception as e:
        print(f"Failed to move {file_path} to unproceed: {e}")

# Function to check if a file's date is after the threshold
def is_wrong_date(file_path):
    try:
        stat = os.stat(file_path)
        file_date = datetime.fromtimestamp(stat.st_mtime)  # Modification time
        return file_date > date_threshold
    except Exception as e:
        print(f"Error checking date for {file_path}: {e}")
        return False

# Function to process the failed log
def process_failed_files():
    if not os.path.exists(failed_log_path):
        print("No failed log file found.")
        return

    with open(failed_log_path, "r") as log_file:
        lines = log_file.readlines()

    for line in lines:
        try:
            parts = line.strip().split(", ")
            json_path = parts[0].split(": ", 1)[1]
            media_file_path = parts[1].split(": ", 1)[1] if "Media:" in parts[1] else None

            # Move JSON file
            move_to_unproceed(json_path)

            # Move media file if it exists
            if media_file_path:
                move_to_unproceed(media_file_path)

        except Exception as e:
            print(f"Error processing failed log entry: {line} - {e}")

# Function to process files in the folder for wrong dates
def process_folder_for_wrong_dates(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Skip the unproceed folder itself
            if unproceed_path in file_path:
                continue

            # Move files with a wrong date
            if is_wrong_date(file_path):
                move_to_unproceed(file_path)

# Run the script
print("Processing failed files...")
process_failed_files()
print("Processing folder for wrong dates...")
process_folder_for_wrong_dates(base_path)
print("Processing complete.")
