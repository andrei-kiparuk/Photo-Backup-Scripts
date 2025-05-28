import os
import shutil
import subprocess
import json
from PIL import Image
from pillow_heif import register_heif_opener
from datetime import datetime
import re
import argparse
import sys

# Register HEIF support with Pillow
register_heif_opener()

# Directory configuration
input_directory = "/Volumes/JBOD/Takeout/GooglePhotos"  # Input Google Takeout folder
output_directory = "/Volumes/JBOD/Converted"  # Output folder for converted files and modified JSONs
processed_directory = "/Volumes/JBOD/Processed"  # Folder for original processed files
metadata_failed_log = "metadata_failed.log"  # Log for metadata errors

# Ensure directories exist
os.makedirs(output_directory, exist_ok=True)
os.makedirs(processed_directory, exist_ok=True)

# Supported file extensions
image_extensions = (
    ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif", ".cr2", ".dng", 
    ".nef", ".arw", ".orf", ".rw2", ".heic", ".webp", ".avif"
)
video_extensions = (
    ".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", 
    ".3gp", ".mts", ".m2ts", ".ts", ".vob", ".ogv", ".m4v"
)

### Utility Functions

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
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
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
    """Extract a date in YYYY/MM/DD format from the file path or filename."""
    # Check for date in path (e.g., 2015/09/06)
    path_pattern = re.compile(r"(\d{4})[\\\/](\d{2})[\\\/](\d{2})")
    match = path_pattern.search(file_path)
    if match:
        try:
            year, month, day = map(int, match.groups())
            return datetime(year, month, day)
        except ValueError:
            pass
    # Check for date in filename (e.g., 20150906-IMG_2331)
    filename = os.path.basename(file_path)
    filename_pattern = re.compile(r"(\d{4})(\d{2})(\d{2})")
    match = filename_pattern.search(filename)
    if match:
        try:
            year, month, day = map(int, match.groups())
            return datetime(year, month, day)
        except ValueError:
            pass
    return None

def get_oldest_datetime(file_path):
    """Get the oldest datetime from metadata, path, or file modification time."""
    metadata_dates = extract_dates_from_metadata(file_path)
    path_date = extract_date_from_path(file_path)
    all_dates = metadata_dates + ([path_date] if path_date else [])
    if all_dates:
        return min(all_dates)
    return datetime.fromtimestamp(os.path.getmtime(file_path))

def set_file_dates(file_path, date_time_obj):
    """Set the file's creation and modification dates using exiftool."""
    try:
        date_str = date_time_obj.strftime("%Y:%m:%d %H:%M:%S")
        subprocess.run(
            ["exiftool", "-overwrite_original", f"-FileModifyDate={date_str}", f"-FileCreateDate={date_str}", file_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(f"Set file dates for {file_path} to {date_str}")
    except Exception as e:
        print(f"Error setting file dates for {file_path}: {e}")

def set_file_dates_from_metadata(file_path, fallback_time):
    """Set file system dates based on metadata dates, with a fallback."""
    date_fields = ["DateTimeOriginal", "CreateDate", "MediaCreateDate", "ContentCreateDate"]
    for field in date_fields:
        try:
            result = subprocess.run(
                ["exiftool", "-s", "-s", "-s", f"-{field}", file_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
            date_str = result.stdout.strip()
            date_time_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            set_file_dates(file_path, date_time_obj)
            return
        except Exception:
            continue
    # Use fallback time if no metadata date is found
    set_file_dates(file_path, fallback_time)
    print(f"No suitable date metadata found for {file_path}, used fallback: {fallback_time}")

def move_to_processed(src, processed_root, date_folder):
    """Move the source file to the processed folder organized by date."""
    try:
        processed_folder = os.path.join(processed_root, date_folder)
        os.makedirs(processed_folder, exist_ok=True)
        destination_path = ensure_unique_filename(os.path.join(processed_folder, os.path.basename(src)))
        shutil.move(src, destination_path)
        print(f"Moved to processed folder: {destination_path}")
    except Exception as e:
        print(f"Error moving file {src} to processed folder: {e}")

### Conversion Functions

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

def convert_video_to_hevc(input_path, output_path, encoder, quality=28):
    """Convert a video to HEVC using FFmpeg with the specified encoder."""
    try:
        output_path = ensure_unique_filename(output_path)
        if encoder == "hevc_nvenc":
            subprocess.run(
                ["ffmpeg", "-i", input_path, "-c:v", "hevc_nvenc", "-rc", "constqp", "-qp", str(quality), "-c:a", "aac", "-tag:v", "hvc1", output_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        elif encoder == "hevc_videotoolbox":
            subprocess.run(
                ["ffmpeg", "-i", input_path, "-c:v", "hevc_videotoolbox", "-qp", str(quality), "-c:a", "aac", "-tag:v", "hvc1", output_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        elif encoder == "libx265":
            subprocess.run(
                ["ffmpeg", "-i", input_path, "-c:v", "libx265", "-crf", str(quality), "-c:a", "aac", "-tag:v", "hvc1", output_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        else:
            raise ValueError(f"Unsupported encoder: {encoder}")

        subprocess.run(
            ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
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

### Metadata and Processing Functions

def log_failure(json_path, media_file_path=None, error=None):
    """Log metadata application failures."""
    with open(metadata_failed_log, "a") as log_file:
        log_file.write(f"JSON: {json_path}, Media: {media_file_path}, Error: {error}\n")

def apply_metadata_from_json(media_file_path, json_path):
    """Apply metadata from JSON to the media file and return capture date."""
    try:
        with open(json_path, "r") as json_file:
            metadata = json.load(json_file)
        
        taken_time = metadata.get("photoTakenTime", {}).get("timestamp")
        if not taken_time or taken_time == "-1":
            taken_time = metadata.get("creationTime", {}).get("timestamp")
        
        if taken_time:
            try:
                if isinstance(taken_time, str) and taken_time.isdigit():
                    date_time_obj = datetime.fromtimestamp(float(taken_time))
                elif isinstance(taken_time, int):
                    date_time_obj = datetime.fromtimestamp(taken_time)
                else:
                    date_time_obj = datetime.fromisoformat(taken_time.replace("Z", "+00:00"))
                date_str = date_time_obj.strftime("%Y:%m:%d %H:%M:%S")
                
                exiftool_command = ["exiftool", "-overwrite_original"]
                exiftool_command.extend([f"-DateTimeOriginal={date_str}", f"-CreateDate={date_str}"])
                
                if "description" in metadata:
                    exiftool_command.extend([f"-Description={metadata['description']}"])
                
                exiftool_command.append(media_file_path)
                subprocess.run(exiftool_command, check=True)
                
                set_file_dates(media_file_path, date_time_obj)
                print(f"Applied metadata to: {media_file_path}")
                return date_time_obj
            except Exception as e:
                log_failure(json_path, media_file_path, f"Invalid date format: {e}")
                return None
        else:
            log_failure(json_path, media_file_path, "Missing both photoTakenTime and creationTime")
            return None
    except Exception as e:
        log_failure(json_path, media_file_path, f"Metadata application error: {e}")
        return None

def process_media_files(input_dir, output_dir, processed_dir, video_encoder, quality=28):
    """Process media files: apply metadata, convert, organize, and handle JSONs."""
    for root, _, files in sorted(os.walk(input_dir), key=lambda x: x[0], reverse=True):
        for file in sorted(files):
            if file.startswith("._") or file.endswith(".json"):
                print(f"Skipping file: {file}")
                continue

            file_path = os.path.join(root, file)
            if not os.path.isfile(file_path):
                continue

            _, ext = os.path.splitext(file)

            try:
                json_path = file_path + ".json"
                capture_date = None
                if os.path.exists(json_path):
                    capture_date = apply_metadata_from_json(file_path, json_path)

                # Get the oldest datetime for fallback
                oldest_datetime = get_oldest_datetime(file_path)

                # Determine date folder and fallback time
                if capture_date:
                    date_folder = capture_date.strftime("%Y/%m/%d")
                    fallback_time = capture_date
                else:
                    date_folder = oldest_datetime.strftime("%Y/%m/%d")
                    fallback_time = oldest_datetime

                output_folder = os.path.join(output_dir, date_folder)
                os.makedirs(output_folder, exist_ok=True)

                # Process media files
                if ext.lower() == ".heic":
                    output_file = copy_file_to_output(file_path, os.path.join(output_folder, file))
                elif ext.lower() in image_extensions:
                    output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.heic")
                    convert_image_to_heic(file_path, output_file)
                elif ext.lower() in video_extensions:
                    if is_video_hevc(file_path):
                        output_file = copy_file_to_output(file_path, os.path.join(output_folder, file))
                    else:
                        output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_hevc.mp4")
                        convert_video_to_hevc(file_path, output_file, encoder=video_encoder, quality=quality)
                else:
                    continue

                # Set output file dates based on metadata, with fallback_time
                set_file_dates_from_metadata(output_file, fallback_time=fallback_time)

                # Handle JSON: Create modified JSON for the output file
                if os.path.exists(json_path):
                    with open(json_path, "r") as json_file:
                        metadata = json.load(json_file)
                    new_json_path = ensure_unique_filename(os.path.join(output_folder, os.path.basename(output_file) + ".json"))
                    metadata["title"] = os.path.basename(output_file)
                    with open(new_json_path, "w") as new_json_file:
                        json.dump(metadata, new_json_file, indent=4)
                    if capture_date:
                        set_file_dates(new_json_path, capture_date)
                    print(f"Created modified JSON: {new_json_path}")

                # Move original files to processed folder
                move_to_processed(file_path, processed_dir, date_folder)
                if os.path.exists(json_path):
                    move_to_processed(json_path, processed_dir, date_folder)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

### Main Execution

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Google Takeout media files.")
    parser.add_argument("--use-gpu", action="store_true", help="Use GPU for video conversion if available.")
    parser.add_argument("--quality", type=int, default=28, help="Quality setting for video conversion (e.g., 20-30 for GPU QP, 18-28 for CPU CRF).")
    args = parser.parse_args()

    def get_available_encoders():
        """Check available FFmpeg encoders."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            encoders = []
            for line in result.stdout.splitlines():
                match = re.match(r"\s*V.{5}\s+(\w+)", line)
                if match:
                    encoders.append(match.group(1))
            return encoders
        except Exception as e:
            print(f"Error getting available encoders: {e}")
            return []

    available_encoders = get_available_encoders()

    # Select GPU encoder based on platform
    if sys.platform == "darwin":  # macOS
        gpu_encoder = "hevc_videotoolbox"
    elif sys.platform == "win32":  # Windows
        gpu_encoder = "hevc_nvenc"
    else:
        gpu_encoder = None

    if args.use_gpu and gpu_encoder and gpu_encoder in available_encoders:
        video_encoder = gpu_encoder
        print(f"Using GPU encoder: {gpu_encoder}")
    else:
        video_encoder = "libx265"
        print("Using CPU encoder: libx265")

    if video_encoder not in available_encoders:
        print(f"Selected encoder {video_encoder} is not available. Please check your FFmpeg installation.")
        exit(1)

    print("Starting Google Takeout media processing...")
    process_media_files(input_directory, output_directory, processed_directory, video_encoder, args.quality)
    print("Processing complete.")