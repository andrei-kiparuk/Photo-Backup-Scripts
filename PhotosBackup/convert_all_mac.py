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
        stat = os.stat(src)
        os.utime(dest, (stat.st_atime, stat.st_mtime))
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

def convert_image_to_heic(input_path, output_path):
    """Convert an image to HEIC format while preserving available metadata."""
    try:
        output_path = ensure_unique_filename(output_path)
        image = Image.open(input_path)
        image.save(output_path, format="HEIF")
        
        # Attempt to copy all available metadata
        try:
            subprocess.run(
                ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            print(f"Image converted and metadata copied: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error copying all metadata for {output_path}: {e}")
            print("Attempting to copy basic metadata only...")
            
            # Fallback to copying basic metadata tags
            subprocess.run(
                [
                    "exiftool",
                    "-overwrite_original",
                    "-tagsFromFile", input_path,
                    "-EXIF:DateTimeOriginal",
                    "-EXIF:CreateDate",
                    "-EXIF:ModifyDate",
                    output_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            print(f"Basic metadata copied successfully: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error copying basic metadata for {output_path}: {e}")
    except Exception as e:
        print(f"Error converting image {input_path}: {e}")

def convert_video_to_hevc(input_path, output_path, target_bitrate="8000k"):
    """Convert a video to HEVC (H.265) format using hardware acceleration (VideoToolbox) on M1/M2 Macs."""
    try:
        output_path = ensure_unique_filename(output_path)
        print(f"Starting hardware-accelerated video conversion: {input_path} -> {output_path}")
        
        # Use VideoToolbox hardware-accelerated HEVC encoding
        subprocess.run(
            [
                "ffmpeg", "-i", input_path, 
                "-c:v", "hevc_videotoolbox",   # Use VideoToolbox for hardware-accelerated HEVC encoding
                "-b:v", target_bitrate,        # Set target bitrate
                "-c:a", "aac",                 # Audio codec
                "-tag:v", "hvc1",              # Tag for HEVC compatibility
                output_path
            ],
            check=True
        )

        # Copy metadata with ExifTool
        try:
            subprocess.run(
                ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
                check=True
            )
            print(f"Video converted and metadata copied: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error copying metadata for video {output_path}: {e}")

    except subprocess.CalledProcessError as e:
        print(f"Error converting video {input_path}: {e}")

def process_media_files(input_dir, output_dir, processed_dir, target_bitrate="8000k"):
    """Process images, RAW files, and videos."""
    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", ".3gp")
    image_extensions = (".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif", ".cr2", ".dng")

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

                if ext.lower() in image_extensions:
                    output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.heic")
                    convert_image_to_heic(file_path, output_file)
                    preserve_timestamps(file_path, output_file)
                    move_to_processed(file_path, processed_dir)

                elif ext.lower() in video_extensions:
                    output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_hevc.mp4")
                    convert_video_to_hevc(file_path, output_file, target_bitrate)
                    preserve_timestamps(file_path, output_file)
                    move_to_processed(file_path, processed_dir)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    input_directory = "/Volumes/T7/Mac/"
    output_directory = "/Volumes/SlowDisk/Converted/"
    processed_directory = "/Volumes/G-DRIVE/processed/"

    # Set the target bitrate here
    target_bitrate = "8000k"

    process_media_files(input_directory, output_directory, processed_directory, target_bitrate)
