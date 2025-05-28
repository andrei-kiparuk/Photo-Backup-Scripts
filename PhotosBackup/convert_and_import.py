import os
import shutil
import subprocess
from PIL import Image
from pillow_heif import register_heif_opener
from datetime import datetime
import re

# Register HEIF support with Pillow
register_heif_opener()

# Directory configuration
input_directory = "/Volumes/G-DRIVE/iCloudExport"
output_directory = "/Volumes/G-DRIVE/Converted"
processed_directory = "/Volumes/G-DRIVE/ProcessedOriginals"
applescript_path = "/Users/akiparuk/Documents/PhotosBackup/import_single_file.applescript"  # Adjust this path

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
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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
    """Get the oldest date from metadata, path, or file modification time."""
    metadata_dates = extract_dates_from_metadata(file_path)
    path_date = extract_date_from_path(file_path)
    all_dates = metadata_dates + ([path_date] if path_date else [])
    if all_dates:
        return min(all_dates).strftime("%Y/%m/%d")
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
        print(f"Moved original to: {destination_path}")
    except Exception as e:
        print(f"Error moving file {src} to processed folder: {e}")

def convert_image_to_heic(input_path, output_path):
    """Convert an image to HEIC format while preserving metadata."""
    try:
        output_path = ensure_unique_filename(output_path)
        image = Image.open(input_path)
        image.save(output_path, format="HEIF")
        subprocess.run(
            ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        print(f"Image converted: {output_path}")
    except Exception as e:
        print(f"Error converting image {input_path}: {e}")

def convert_video_to_hevc(input_path, output_path, quality=50):
    """Convert a video to HEVC using hardware acceleration."""
    try:
        output_path = ensure_unique_filename(output_path)
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-c:v", "hevc_videotoolbox", "-q:v", str(quality), "-c:a", "aac", "-tag:v", "hvc1", output_path],
            check=True
        )
        subprocess.run(
            ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
            check=True
        )
        print(f"Video converted: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video {input_path}: {e}")

def is_video_hevc(file_path):
    """Check if the video is encoded in HEVC."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        codec = result.stdout.strip().lower()
        return codec in ["hevc", "h265"]
    except Exception:
        return False

def copy_file_to_output(input_path, output_path):
    """Copy file to output directory and preserve timestamps."""
    output_path = ensure_unique_filename(output_path)
    shutil.copy2(input_path, output_path)
    print(f"Copied to: {output_path}")
    return output_path

def process_media_files(input_dir, output_dir, processed_dir, quality=90):
    """Process media files one by one, convert, and import."""
    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", ".3gp")
    image_extensions = (".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".cr2", ".dng", ".heic")

    for root, _, files in sorted(os.walk(input_dir), key=lambda x: x[0], reverse=True):
        for file in sorted(files):
            if file.startswith("._"):
                print(f"Skipping file: {file}")
                continue

            file_path = os.path.join(root, file)
            if not os.path.isfile(file_path):
                continue

            _, ext = os.path.splitext(file)

            try:
                date_folder = get_oldest_date(file_path)
                output_folder = os.path.join(output_dir, date_folder)
                os.makedirs(output_folder, exist_ok=True)

                if ext.lower() == ".heic":
                    output_file = os.path.join(output_folder, file)
                    output_file = copy_file_to_output(file_path, output_file)
                elif ext.lower() in image_extensions:
                    output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.heic")
                    convert_image_to_heic(file_path, output_file)
                    preserve_timestamps(file_path, output_file)
                elif ext.lower() in video_extensions:
                    if is_video_hevc(file_path):
                        output_file = os.path.join(output_folder, file)
                        output_file = copy_file_to_output(file_path, output_file)
                    else:
                        output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_hevc.mp4")
                        convert_video_to_hevc(file_path, output_file, quality=quality)
                        preserve_timestamps(file_path, output_file)
                else:
                    continue

                # Move original file after conversion
                move_to_processed(file_path, processed_dir)

                # Call AppleScript to import the converted file
                subprocess.run(["osascript", applescript_path, output_file])
                print(f"Processed and sent to import: {output_file}")

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    quality = 90  # Adjust as needed
    process_media_files(input_directory, output_directory, processed_directory, quality)