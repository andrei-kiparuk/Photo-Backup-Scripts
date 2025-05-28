import os
import shutil
import exiftool
from pathlib import Path
from datetime import datetime

# Define the base directory for source and destination
base_dir = "/Volumes/SlowDisk/Icloud"

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

def get_date_from_filename(filename):
    # Extract the date from the filename (formats: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, or WP_YYYYMMDD)
    try:
        # Check for YYYY-MM-DD format (e.g., 2013-07-09 12.16.44.mp4)
        if filename.startswith(tuple(f"{year}-{month:02d}-{day:02d}" for year in range(2000, 2030) for month in range(1, 13) for day in range(1, 32))):
            date_part = filename[:10]  # First 10 characters: YYYY-MM-DD
            year, month, day = date_part.split("-")
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")

        # Check for WP_YYYYMMDD format (e.g., WP_20151026_10_15_40_Pro.mp4)
        if filename.startswith("WP_") and len(filename) > 11:  # WP_ + 8 chars for YYYYMMDD
            date_part = filename[3:11]  # Extract YYYYMMDD after WP_
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")

        # Check for YYYYMMDD format (e.g., 20180804_025359000_iOS.mp4)
        if filename.startswith(tuple(f"{year}{month:02d}{day:02d}" for year in range(2000, 2030) for month in range(1, 13) for day in range(1, 32))):
            date_part = filename[:8]  # First 8 characters: YYYYMMDD
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")

        # Check for YYYY_MM_DD format (e.g., 2016_01_01_...)
        if "_" in filename:
            date_part = filename.split("_", 3)[:3]  # Split on "_" and take first 3 parts
            if len(date_part) == 3 and len(date_part[0]) == 4 and len(date_part[1]) == 2 and len(date_part[2]) == 2:
                year, month, day = date_part
                # Validate that year, month, and day are numeric and within reasonable ranges
                if (year.isdigit() and month.isdigit() and day.isdigit() and
                    2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                    return datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")
        return None
    except (ValueError, IndexError):
        return None

def get_folder_date(filepath):
    # Extract the folder date from the path (e.g., /Volumes/SlowDisk/Icloud/2015/06/02)
    parts = filepath.split(os.sep)
    try:
        # Look for YYYY/MM/DD in the path
        for i in range(len(parts) - 3):
            if (parts[i + 0].isdigit() and len(parts[i + 0]) == 4 and
                parts[i + 1].isdigit() and len(parts[i + 1]) == 2 and
                parts[i + 2].isdigit() and len(parts[i + 2]) == 2):
                year, month, day = parts[i + 0], parts[i + 1], parts[i + 2]
                return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    except ValueError:
        pass
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
    return os.path.join(base_dir, year, month, day)

def ensure_folder_exists(folder_path):
    # Create the folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def organize_videos():
    # Walk through all files in the base directory
    for root, _, files in os.walk(base_dir):
        for filename in files:
            # Skip files that don't match the expected format
            if not filename.lower().endswith(supported_extensions):
                continue

            filepath = os.path.join(root, filename)

            # Get dates from all sources
            folder_date = get_folder_date(filepath)
            filename_date = get_date_from_filename(filename)
            content_created_date = get_content_created_date(filepath)

            # Collect all valid dates
            dates = [d for d in [folder_date, filename_date, content_created_date] if d]
            if not dates:
                print(f"Keeping {filename} in place: No valid dates found")
                continue

            # Find the earliest date
            earliest_date = min(dates)
            print(f"Earliest date for {filename}: {earliest_date} (Folder: {folder_date}, Filename: {filename_date}, Content Created: {content_created_date})")

            # Get the current folder and the correct folder
            current_folder = root
            correct_folder = get_correct_folder(earliest_date)

            # Check if the file is already in the correct folder
            if current_folder == correct_folder:
                print(f"{filename} is already in the correct folder: {current_folder}")
                continue

            # Ensure the correct folder exists
            ensure_folder_exists(correct_folder)

            # Define the current and new file paths
            new_path = os.path.join(correct_folder, filename)

            # Check for conflicts
            if os.path.exists(new_path):
                print(f"Conflict: {filename} already exists in {correct_folder}. Skipping move.")
                continue

            # Move the file
            try:
                shutil.move(filepath, new_path)
                print(f"Moved {filename} from {current_folder} to {correct_folder}")
            except Exception as e:
                print(f"Error moving {filename}: {e}")

if __name__ == "__main__":
    organize_videos()