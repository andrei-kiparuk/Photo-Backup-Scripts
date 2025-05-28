import os
import shutil
from pathlib import Path

# Define the base directory and subfolders to process
base_dir = "/Volumes/SlowDisk/toimport"
subfolders = ["3gp", "cr2", "dng", "heic", "jpeg", "jpg", "psd", "tif", "tiff"]

# Define supported file extensions for each folder type
supported_extensions = (".3gp", ".cr2", ".dng", ".heic", ".jpeg", ".jpg", ".json", ".psd", ".tif", ".tiff")

def get_date_from_filename(filename):
    # Extract the date from the filename (formats: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, or WP_YYYYMMDD)
    try:
        # Check for YYYY-MM-DD format (e.g., 2013-07-09 12.16.44.jpg)
        if filename.startswith(tuple(f"{year}-{month:02d}-{day:02d}" for year in range(2000, 2030) for month in range(1, 13) for day in range(1, 32))):
            date_part = filename[:10]  # First 10 characters: YYYY-MM-DD
            year, month, day = date_part.split("-")
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return year, month, day

        # Check for WP_YYYYMMDD format (e.g., WP_20151026_10_15_40_Pro.jpg)
        if filename.startswith("WP_") and len(filename) > 11:  # WP_ + 8 chars for YYYYMMDD
            date_part = filename[3:11]  # Extract YYYYMMDD after WP_
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            if (year.isdigit() and month.isdigit() and day.isdigit() and
                2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                return year, month, day

        # Check for YYYYMMDD format (e.g., 20180804_025359000_iOS.jpg)
        if filename.startswith(tuple(f"{year}{month:02d}{day:02d}" for year in range(2000, 2030) for month in range(1, 13) for day in range(1, 32))):
            date_part = filename[:8]  # First 8 characters: YYYYMMDD
            year = date_part[:4]
            month = date_part[4:6]
            day = date_part[6:8]
            return year, month, day

        # Check for YYYY_MM_DD format (e.g., 2016_01_01_...)
        if "_" in filename:
            date_part = filename.split("_", 3)[:3]  # Split on "_" and take first 3 parts
            if len(date_part) == 3 and len(date_part[0]) == 4 and len(date_part[1]) == 2 and len(date_part[2]) == 2:
                year, month, day = date_part
                # Validate that year, month, and day are numeric and within reasonable ranges
                if (year.isdigit() and month.isdigit() and day.isdigit() and
                    2000 <= int(year) <= 2030 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                    return year, month, day
        return None
    except (ValueError, IndexError):
        return None

def get_correct_folder(year, month, day, subfolder):
    # Construct the correct folder path based on the date and subfolder
    return os.path.join(base_dir, subfolder, year, month, day)

def ensure_folder_exists(folder_path):
    # Create the folder if it doesn't exist
    Path(folder_path).mkdir(parents=True, exist_ok=True)

def move_files():
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

                # Extract the date from the filename
                date = get_date_from_filename(filename)
                if not date:
                    print(f"Skipping {filename} in {subfolder}: Invalid date format")
                    continue

                year, month, day = date

                # Get the current folder and the correct folder
                current_folder = root
                correct_folder = get_correct_folder(year, month, day, subfolder)

                # Check if the file is already in the correct folder
                if current_folder == correct_folder:
                    continue

                # Ensure the correct folder exists
                ensure_folder_exists(correct_folder)

                # Define the current and new file paths
                current_path = os.path.join(current_folder, filename)
                new_path = os.path.join(correct_folder, filename)

                # Check if a file with the same name already exists in the target folder
                if os.path.exists(new_path):
                    print(f"Conflict: {filename} already exists in {correct_folder}. Skipping.")
                    continue

                # Move the file
                try:
                    shutil.move(current_path, new_path)
                    print(f"Moved {filename} from {current_folder} to {correct_folder}")
                except Exception as e:
                    print(f"Error moving {filename}: {e}")

if __name__ == "__main__":
    move_files()