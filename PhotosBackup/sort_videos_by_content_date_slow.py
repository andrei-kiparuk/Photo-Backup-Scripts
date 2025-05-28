import os
import shutil
import exiftool
from pathlib import Path
from datetime import datetime

# Define the source and destination directories
source_dir = "/Volumes/SlowDisk/UnsortedPhotos"
dest_base_dir = "/Volumes/G-DRIVE/sortedvideos"

# Define supported file extensions for videos
supported_extensions = (".mp4", ".mov", ".avi", ".mkv", ".wmv", ".3gp")

def parse_date(date_str):
    # Parse dates in various formats (e.g., "2015:06:02 17:53:00")
    try:
        # Handle sub-second precision (e.g., "2016:06:11 21:20:49.35")
        if "." in date_str and date_str.count(":") >= 2:  # Check for sub-second part
            date_str = date_str.split(".")[0]  # Remove sub-second part (e.g., ".35")
        # Handle exiftool's default format with timezone (e.g., "2015:06:02 17:53:00-06:00")
        if "+" in date_str or "-" in date_str[-6:]:
            date_str = date_str[:-6]  # Remove timezone offset (e.g., "-06:00")
        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

def get_content_created_date(filepath):
    # Get Content Created date using exiftool
    with exiftool.ExifToolHelper() as et:
        try:
            metadata = et.get_metadata(filepath)[0]
            # Try content-specific tags first, prioritizing video-specific tags
            content_created = None
            content_tags = [
                "QuickTime:CreateDate",  # Common for video files
                "QuickTime:MediaCreateDate",
                "EXIF:DateTimeOriginal",
                "EXIF:CreateDate",
                "EXIF:ModifyDate",
                "EXIF:SubSecCreateDate",
                "EXIF:SubSecDateTimeOriginal",
                "EXIF:SubSecModifyDate",
            ]
            for tag in content_tags:
                if tag in metadata:
                    content_created = parse_date(metadata[tag])
                    if content_created:
                        print(f"Found Content Created date for {filepath} in {tag}: {content_created}")
                        break
            if not content_created:
                # Print available date-related tags for debugging
                print(f"No Content Created date found for {filepath}. Available date tags:")
                for key, value in metadata.items():
                    if "date" in key.lower() or "time" in key.lower():
                        print(f"  {key}: {value}")
            return content_created
        except Exception as e:
            print(f"Error reading metadata for {filepath}: {e}")
            return None

def get_correct_folder(content_created):
    # Construct the correct folder path based on the Content Created date
    year = content_created.strftime("%Y")
    month = content_created.strftime("%m")
    day = content_created.strftime("%d")
    return os.path.join(dest_base_dir, year, month, day)

def ensure_folder_exists(folder_path):
    # Create the folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def sort_videos():
    # Walk through all files in the source directory
    for root, _, files in os.walk(source_dir):
        for filename in files:
            # Skip files that don't match the expected format
            if not filename.lower().endswith(supported_extensions):
                continue

            filepath = os.path.join(root, filename)
            # Get the Content Created date
            content_created = get_content_created_date(filepath)
            if not content_created:
                print(f"Keeping {filename} in place: No Content Created date found")
                continue

            # Determine the correct destination folder
            correct_folder = get_correct_folder(content_created)
            print(f"Destination folder for {filename}: {correct_folder}")
            ensure_folder_exists(correct_folder)
            new_path = os.path.join(correct_folder, filename)

            # Check for conflicts
            if os.path.exists(new_path):
                print(f"Conflict: {filename} already exists in {correct_folder}. Skipping move.")
                continue

            # Move the file
            try:
                shutil.move(filepath, new_path)
                print(f"Moved {filename} from {root} to {correct_folder}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")

if __name__ == "__main__":
    sort_videos()