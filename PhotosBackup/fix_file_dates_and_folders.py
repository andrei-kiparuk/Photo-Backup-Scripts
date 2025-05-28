import os
import shutil
import exiftool
from pathlib import Path
from datetime import datetime
import time

# Define the base directory and subfolders to process
base_dir = "/Volumes/SlowDisk/toimport"
subfolders = ["3gp", "cr2", "dng", "heic", "jpeg", "jpg", "psd", "tif", "tiff"]

# Define supported file extensions for each folder type
supported_extensions = (".3gp", ".cr2", ".dng", ".heic", ".jpeg", ".jpg", ".json", ".psd", ".tif", ".tiff")

def parse_date(date_str):
    # Parse dates in various formats (e.g., "Jun 2, 2015 at 5:53 PM" or "2015:06:02 17:53:00")
    try:
        # Handle "Jun 2, 2015 at 5:53 PM" format
        if " at " in date_str:
            date_str = date_str.replace(" at ", " ").replace(",", "")
            return datetime.strptime(date_str, "%b %d %Y %I:%M %p")
        # Handle sub-second precision (e.g., "2016:06:11 21:20:49.35")
        if "." in date_str and date_str.count(":") >= 2:  # Check for sub-second part in a date with at least date and time colons
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
        # Check for YYYY-MM-DD format (e.g., 2013-07-09 12.16.44.jpg)
        if filename.startswith(tuple(f"{year}-{month:02d}-{day:02d}" for year in range(2000, 2030) for month in range(1, 13) for day in range(1, 32))):
            date_part = filename[:10]  # First 10 characters: YYYY-MM-DD
            year, month, day = date_part.split("-")
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")

        # Check for WP_YYYYMMDD format (e.g., WP_20151026_10_15_40_Pro.jpg)
        if filename.startswith("WP_") and len(filename) > 11:  # WP_ + 8 chars for YYYYMMDD
            date_part = filename[3:11]  # Extract YYYYMMDD after WP_
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return datetime.strptime(f"{year}-{month}-{day} 00:00:00", "%Y-%m-%d %H:%M:%S")

        # Check for YYYYMMDD format (e.g., 20180804_025359000_iOS.jpg)
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

def get_file_dates(filepath):
    # Get Created, Modified, and Content Created dates using exiftool
    with exiftool.ExifToolHelper() as et:
        try:
            metadata = et.get_metadata(filepath)[0]
            # Get filesystem dates
            created = datetime.fromtimestamp(os.path.getctime(filepath))
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            # Get Content Created date from metadata (try content-specific tags first)
            content_created = None
            content_tags = [
                "EXIF:DateTimeOriginal",
                "EXIF:CreateDate",
                "EXIF:ModifyDate",
                "QuickTime:CreateDate",
                "EXIF:SubSecCreateDate",
                "EXIF:SubSecDateTimeOriginal",
                "EXIF:SubSecModifyDate",
            ]
            # Try content-specific tags first
            for tag in content_tags:
                if tag in metadata:
                    content_created = parse_date(metadata[tag])
                    if content_created:
                        print(f"Found Content Created date in {tag}: {content_created}")
                        break
            # Only use File:File* tags as a last resort
            if not content_created:
                file_tags = [
                    "File:FileCreateDate",
                    "File:FileModifyDate",
                ]
                for tag in file_tags:
                    if tag in metadata:
                        content_created = parse_date(metadata[tag])
                        if content_created:
                            print(f"Found Content Created date in {tag}: {content_created} (filesystem date, may not be accurate)")
                            break
            if not content_created:
                # Print available date-related tags for debugging
                print(f"No Content Created date found for {filepath}. Available date tags:")
                for key, value in metadata.items():
                    if "date" in key.lower() or "time" in key.lower():
                        print(f"  {key}: {value}")
            return created, modified, content_created
        except Exception as e:
            print(f"Error reading metadata for {filepath}: {e}")
            return None, None, None

def get_folder_date(filepath):
    # Extract the folder date from the path (e.g., /Volumes/SlowDisk/toimport/cr2/2015/06/02)
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

def set_file_dates(filepath, target_date):
    # Set the Created and Modified dates on the filesystem
    timestamp = int(target_date.timestamp())
    os.utime(filepath, (timestamp, timestamp))
    # Update metadata dates using exiftool
    with exiftool.ExifToolHelper() as et:
        try:
            date_str = target_date.strftime("%Y:%m:%d %H:%M:%S")
            et.set_tags(
                [filepath],
                tags={
                    "EXIF:DateTimeOriginal": date_str,
                    "EXIF:CreateDate": date_str,
                    "EXIF:ModifyDate": date_str,
                    "File:FileCreateDate": date_str,
                    "File:FileModifyDate": date_str
                }
            )
        except Exception as e:
            print(f"Error setting metadata for {filepath}: {e}")

def get_correct_folder(year, month, day, subfolder):
    # Construct the correct folder path based on the date and subfolder
    return os.path.join(base_dir, subfolder, year, month, day)

def ensure_folder_exists(folder_path):
    # Create the folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def fix_file_dates_and_folders():
    # Process each subfolder
    for subfolder in subfolders:
        subfolder_path = os.path.join(base_dir, subfolder)
        if not os.path.exists(subfolder_path):
            print(f"Subfolder {subfolder_path} does not exist. Skipping.")
            continue

        # Walk through all folders in the subfolder
        for root, _, files in os.walk(subfolder_path):
            for filename in files:
                # Skip files that don't match the expected format
                if not filename.lower().endswith(supported_extensions):
                    continue

                filepath = os.path.join(root, filename)
                # Get the dates
                created, modified, content_created = get_file_dates(filepath)

                # If no Content Created date is found, fall back to the filename date
                if not content_created:
                    content_created = get_date_from_filename(filename)
                    if content_created:
                        print(f"Using filename date for {filename}: {content_created}")
                    else:
                        print(f"Skipping {filename} in {subfolder}: No Content Created date found and no valid date in filename")
                        continue

                folder_date = get_folder_date(filepath)
                if not folder_date:
                    print(f"Skipping {filename} in {subfolder}: Could not determine folder date")
                    continue

                # Find the earliest date
                dates = [d for d in [created, modified, folder_date] if d]
                if not dates:
                    print(f"Skipping {filename} in {subfolder}: No valid dates to compare")
                    continue

                earliest_date = min(dates + [content_created])

                # If Content Created is the earliest, update everything
                if content_created == earliest_date and content_created < min(dates):
                    print(f"Fixing {filename} in {subfolder}: Content Created ({content_created}) is earliest")
                    # Update filesystem and metadata dates
                    set_file_dates(filepath, content_created)
                    # Move to correct folder
                    year = content_created.strftime("%Y")
                    month = content_created.strftime("%m")
                    day = content_created.strftime("%d")
                    correct_folder = get_correct_folder(year, month, day, subfolder)
                    print(f"Destination folder: {correct_folder}")
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
    fix_file_dates_and_folders()