import os
import shutil
import subprocess
from PIL import Image
from pillow_heif import register_heif_opener
from datetime import datetime
import re

# Register HEIF support with Pillow
register_heif_opener()

CORRUPTED_LOG = "corrupted_videos.log"

def ensure_unique_filename(output_path):
    """Add a numeric suffix to the filename if it already exists."""
    if not os.path.exists(output_path):
        return output_path

    base, ext = os.path.splitext(output_path)
    counter = 1
    new_output_path = f"{base}_{counter}{ext}"

    while os.path.exists(new_output_path):
        counter += 1
        new_output_path = f"{base}_{counter}{ext}"

    return new_output_path

def extract_dates_from_metadata(file_path):
    """Extract possible dates from metadata using ExifTool."""
    try:
        result = subprocess.run(
            ["exiftool", "-s", "-s", "-s", "-CreateDate", "-DateTimeOriginal", "-MediaCreateDate", "-ContentCreateDate", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        dates = []
        for line in result.stdout.splitlines():
            try:
                date = datetime.strptime(line.strip(), "%Y:%m:%d %H:%M:%S")
                dates.append(date)
            except ValueError:
                pass
        return dates
    except Exception as e:
        print(f"Error extracting metadata dates from {file_path}: {e}")
        return []

def extract_date_from_path(file_path):
    """Extract a date in YYYY/MM/DD format from the file path."""
    path_pattern = re.compile(r"(\d{4})/(\d{2})/(\d{2})")
    match = path_pattern.search(file_path)
    if match:
        try:
            year, month, day = map(int, match.groups())
            return datetime(year, month, day)
        except ValueError:
            pass
    return None

def get_oldest_date(file_path):
    """Get the oldest date from metadata or the file path."""
    metadata_dates = extract_dates_from_metadata(file_path)
    path_date = extract_date_from_path(file_path)
    all_dates = metadata_dates + ([path_date] if path_date else [])
    
    if all_dates:
        oldest_date = min(all_dates)
        return oldest_date.strftime("%Y/%m/%d")
    else:
        # Fallback to file's modification date
        return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y/%m/%d")

def preserve_timestamps(src, dest):
    """Preserve the original file's creation and modification timestamps."""
    try:
        # stat = os.stat(src)
        # os.utime(dest, (stat.st_atime, stat.st_mtime))
        print(f"Skip preserving timestamps for {dest}")
    except Exception as e:
        print(f"Error preserving timestamps for {dest}: {e}")

def move_to_processed(src, processed_root):
    """Move the source file to the processed folder organized by date."""
    try:
        date_folder = get_oldest_date(src)
        processed_folder = os.path.join(processed_root, date_folder)
        os.makedirs(processed_folder, exist_ok=True)
        destination_path = ensure_unique_filename(os.path.join(processed_folder, os.path.basename(src)))
        shutil.move(src, destination_path)
        print(f"Moved to processed folder: {destination_path}")
    except Exception as e:
        print(f"Error moving file {src} to processed folder: {e}")



def process_media_files(input_dir, output_dir, processed_dir, target_bitrate="8000k"):

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.startswith("._"):
                print(f"Skipping file: {file}")
                continue

            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)

            try:
                date_folder = get_oldest_date(file_path)
                output_folder = os.path.join(output_dir, date_folder)
                os.makedirs(output_folder, exist_ok=True)
                output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.heic")
                move_to_processed(file_path, processed_dir)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    input_directory = "/Volumes/G-DRIVE/unpack/"
    output_directory = "/Volumes/SlowDisk/Converted/"
    processed_directory = "/Volumes/G-DRIVE/processed/"

    # Set the target bitrate here
    target_bitrate = "8000k"

    process_media_files(input_directory, output_directory, processed_directory, target_bitrate)
