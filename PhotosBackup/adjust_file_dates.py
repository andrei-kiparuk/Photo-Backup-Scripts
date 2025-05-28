import os
import datetime
import pathlib
import platform
from datetime import datetime as dt

def get_file_timestamp(file_path):
    """Get creation and modification timestamps of a file."""
    stat = os.stat(file_path)
    if platform.system() == "Windows":
        creation_time = stat.st_ctime
    else:
        creation_time = stat.st_birthtime if hasattr(stat, 'st_birthtime') else stat.st_mtime
    return creation_time, stat.st_mtime

def set_file_timestamp(file_path, new_date, original_time):
    """Set file creation and modification timestamps, preserving original time."""
    # Combine folder date with original time
    original_datetime = dt.fromtimestamp(original_time)
    new_datetime = dt(
        new_date.year,
        new_date.month,
        new_date.day,
        original_datetime.hour,
        original_datetime.minute,
        original_datetime.second,
        original_datetime.microsecond
    )
    
    new_timestamp = new_datetime.timestamp()
    
    # Set both modification and access times
    os.utime(file_path, (new_timestamp, new_timestamp))
    
    # On Windows, set creation time using pathlib (if available)
    if platform.system() == "Windows":
        try:
            path = pathlib.Path(file_path)
            path.touch()
            # Note: Windows creation time setting might require additional permissions
        except Exception as e:
            print(f"Warning: Could not set creation time for {file_path}: {e}")

def process_directory(root_dir):
    """Process all files in the directory structure YYYY/MM/DD."""
    # Define supported file extensions for photos and videos
    photo_extensions = (".jpg", ".jpeg", ".png", ".cr2", ".dng", ".heic", ".tif", ".tiff")
    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".m4v", ".wmv", ".3gp")
    valid_extensions = photo_extensions + video_extensions

    for root, _, files in os.walk(root_dir):
        # Extract date from folder path
        try:
            # Split path and get last three components (YYYY/MM/DD)
            path_parts = root.split(os.sep)[-3:]
            if len(path_parts) >= 3:
                year, month, day = map(int, path_parts)
                folder_date = datetime.date(year, month, day)
            else:
                print(f"Skipping {root}: Not in YYYY/MM/DD format")
                continue
        except ValueError:
            print(f"Skipping {root}: Invalid date format")
            continue

        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Check if file is a photo or video (based on specified extensions)
            if not file_name.lower().endswith(valid_extensions):
                continue

            # Get file timestamps
            creation_time, modification_time = get_file_timestamp(file_path)
            file_creation_date = dt.fromtimestamp(creation_time).date()
            file_modification_date = dt.fromtimestamp(modification_time).date()

            # Compare dates and update if different
            if file_creation_date != folder_date:
                print(f"Updating creation date for {file_path}: {file_creation_date} -> {folder_date}")
                set_file_timestamp(file_path, folder_date, creation_time)
            
            if file_modification_date != folder_date:
                print(f"Updating modification date for {file_path}: {file_modification_date} -> {folder_date}")
                set_file_timestamp(file_path, folder_date, modification_time)

if __name__ == "__main__":
    # Specify the root directory containing YYYY/MM/DD structure
    root_directory = "/Volumes/T7/inprocess"
    
    if not os.path.exists(root_directory):
        print(f"Error: Directory {root_directory} does not exist")
    else:
        print(f"Processing files in {root_directory}")
        process_directory(root_directory)
        print("Processing complete")