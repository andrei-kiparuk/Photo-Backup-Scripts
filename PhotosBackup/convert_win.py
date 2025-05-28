import os
import shutil
import subprocess
from PIL import Image
from pillow_heif import register_heif_opener
from datetime import datetime
import sys

# Register HEIF support with Pillow
register_heif_opener()

CORRUPTED_LOG = "corrupted_videos.log"

# Directories
input_directory = "V:\\Mac"
output_directory = "Y:\\Converted"
processed_directory = "Z:\\processed"

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

def is_video_corrupted(file_path):
    """Check if the video file is corrupted using ffprobe."""
    ffprobe_cmd = "ffprobe.exe" if sys.platform == "win32" else "ffprobe"
    try:
        result = subprocess.run(
            [ffprobe_cmd, "-v", "error", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            with open(CORRUPTED_LOG, "a") as log:
                log.write(f"Corrupted file: {file_path}\n")
            print(f"Corrupted video detected: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error checking file integrity for {file_path}: {e}")
        return True

def preserve_timestamps(src, dest):
    """Preserve the original file's creation and modification timestamps."""
    try:
        stat = os.stat(src)
        if sys.platform == "win32":
            creation_time = stat.st_ctime
            os.utime(dest, (creation_time, stat.st_mtime))
        else:
            os.utime(dest, (stat.st_atime, stat.st_mtime))
    except Exception as e:
        print(f"Error preserving timestamps for {dest}: {e}")

def get_date_folder(file_path):
    """Get the date folder path in YYYY/MM/DD format based on file creation date."""
    creation_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    return os.path.join(creation_time.strftime("%Y"), creation_time.strftime("%m"), creation_time.strftime("%d"))

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

def convert_video_to_hevc(src, dest_folder):
    """Convert a video to HEVC format using FFmpeg and save it to the destination folder."""
    ffmpeg_cmd = "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
    dest_path = os.path.join(dest_folder, os.path.splitext(os.path.basename(src))[0] + ".mp4")
    dest_path = ensure_unique_filename(dest_path)
    try:
        subprocess.run([
            ffmpeg_cmd, "-i", src, "-c:v", "libx265", "-crf", "28", dest_path
        ], check=True)
        preserve_timestamps(src, dest_path)
        print(f"Converted and saved video to {dest_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video {src} to HEVC: {e}")

def process_files(input_dir, output_dir, processed_dir):
    """Process all photos and videos in the input directory and subdirectories."""
    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            date_folder = get_date_folder(file_path)
            output_folder = os.path.join(output_dir, date_folder)
            os.makedirs(output_folder, exist_ok=True)

            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.heif')):
                convert_image_to_heic(file_path, output_folder)
            elif file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                if not is_video_corrupted(file_path):
                    convert_video_to_hevc(file_path, output_folder)

            # Move original to processed directory
            processed_folder = os.path.join(processed_dir, date_folder)
            os.makedirs(processed_folder, exist_ok=True)
            processed_path = os.path.join(processed_folder, os.path.basename(file_path))
            shutil.move(file_path, processed_path)
            print(f"Moved original file to {processed_path}")

def main():
    process_files(input_directory, output_directory, processed_directory)

if __name__ == "__main__":
    main()
