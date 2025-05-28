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
            ["exiftool", "-s", "-s", "-s",
             "-CreateDate", "-DateTimeOriginal",
             "-MediaCreateDate", "-ContentCreateDate",
             file_path],
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
    """Preserve the original file's creation and modification timestamps (POSIX)."""
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
        destination_path = ensure_unique_filename(
            os.path.join(processed_folder, os.path.basename(src))
        )
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

def is_video_hevc(file_path):
    """Check if the video is encoded in HEVC using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        codec = result.stdout.strip().lower()
        return codec in ["hevc", "h265"]
    except Exception as e:
        print(f"Error checking if video is HEVC: {e}")
        return False

def copy_file_to_output(input_path, output_path):
    """Copy file to output directory and preserve timestamps."""
    output_path = ensure_unique_filename(output_path)
    shutil.copy2(input_path, output_path)
    print(f"File already in target format. Copied to: {output_path}")
    return output_path

def process_media_files(input_dir, output_dir, processed_dir, target_bitrate="8000k"):
    """Process images, RAW files, and videos in ascending chronological order (YYYY/MM/DD)."""
    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", ".3gp", ".mts", ".m4v")
    image_extensions = (".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif", ".cr2", ".dng", ".heic")

    # Collect all date directories in the format YYYY/MM/DD
    directories_with_dates = []
    for year_dir in sorted(os.listdir(input_dir)):
        year_path = os.path.join(input_dir, year_dir)
        if not year_dir.isdigit() or len(year_dir) != 4:
            continue
        for month_dir in sorted(os.listdir(year_path)):
            month_path = os.path.join(year_path, month_dir)
            if not month_dir.isdigit() or len(month_dir) != 2:
                continue
            for day_dir in sorted(os.listdir(month_path)):
                day_path = os.path.join(month_path, day_dir)
                if not day_dir.isdigit() or len(day_dir) != 2:
                    continue
                # We have a directory structured as YYYY/MM/DD
                try:
                    date_obj = datetime(int(year_dir), int(month_dir), int(day_dir))
                    directories_with_dates.append((date_obj, day_path))
                except ValueError:
                    # Invalid date
                    pass

    # Sort directories by date in ascending order
    directories_with_dates.sort(key=lambda x: x[0], reverse=False)

    # Process files in these directories
    for date_obj, dir_path in directories_with_dates:
        date_folder = date_obj.strftime("%Y/%m/%d")  # We'll use this for fix_metadata_date
        for file in os.listdir(dir_path):
            if file.startswith("._"):
                print(f"Skipping file: {file}")
                continue

            file_path = os.path.join(dir_path, file)
            if not os.path.isfile(file_path):
                continue

            _, ext = os.path.splitext(file)

            try:
                # We'll also re-check the oldest date, just in case
                date_folder = get_oldest_date(file_path)  # "YYYY/MM/DD" from either metadata or path
                output_folder = os.path.join(output_dir, date_folder)
                os.makedirs(output_folder, exist_ok=True)

                # If image is already HEIC
                if ext.lower() == ".heic":
                    output_file = os.path.join(output_folder, file)
                    output_file = copy_file_to_output(file_path, output_file)
                    preserve_timestamps(file_path, output_file)
                    # NEW: Fix metadata date
                    fix_metadata_date(output_file, date_folder)

                    move_to_processed(file_path, processed_dir)
                    continue

                # If it's an image (non-HEIC)
                if ext.lower() in image_extensions and ext.lower() != ".heic":
                    # Convert to HEIC
                    output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.heic")
                    convert_image_to_heic(file_path, output_file)
                    preserve_timestamps(file_path, output_file)
                    # NEW: Fix metadata date
                    fix_metadata_date(output_file, date_folder)

                    move_to_processed(file_path, processed_dir)

                # If it's a video
                elif ext.lower() in video_extensions:
                    # Check if the video is already HEVC
                    if is_video_hevc(file_path):
                        # Just copy it
                        output_file = os.path.join(output_folder, file)
                        output_file = copy_file_to_output(file_path, output_file)
                        preserve_timestamps(file_path, output_file)
                        # NEW: Fix metadata date
                        fix_metadata_date(output_file, date_folder)

                        move_to_processed(file_path, processed_dir)
                    else:
                        # Convert to HEVC
                        output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_hevc.mp4")
                        convert_video_to_hevc(file_path, output_file, target_bitrate)
                        preserve_timestamps(file_path, output_file)
                        # NEW: Fix metadata date
                        fix_metadata_date(output_file, date_folder)

                        move_to_processed(file_path, processed_dir)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

#
# NEW HELPER FUNCTIONS FOR FIXING METADATA & FILESYSTEM DATES
#

def fix_metadata_date(file_path, folder_date_str):
    """
    Ensure the file's metadata and file-system creation date match the 'folder_date_str' (YYYY/MM/DD).
    Keep the same time from the file's metadata if possible; otherwise default to 00:00:00.

    On macOS, also adjusts the file's 'creation date' using SetFile (Xcode Command Line Tools).
    """
    # folder_date_str is something like '2023/08/25'
    # Parse into year, month, day
    try:
        folder_year, folder_month, folder_day = folder_date_str.split('/')
        folder_year, folder_month, folder_day = int(folder_year), int(folder_month), int(folder_day)
    except ValueError:
        print(f"Could not parse folder date: {folder_date_str}")
        return

    # Convert folder_date_str into 'YYYY:MM:DD' format
    folder_exif_date = f"{folder_year:04d}:{folder_month:02d}:{folder_day:02d}"

    # 1) Read existing metadata date/time from the file (if any).
    try:
        result = subprocess.run(
            ["exiftool", "-s3", "-DateTimeOriginal", "-CreateDate", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lines = result.stdout.strip().splitlines()

        metadata_datetime_str = None
        # exiftool might print 1 or 2 lines
        for ln in lines:
            ln = ln.strip()
            # if it looks like "YYYY:MM:DD HH:MM:SS"
            if re.match(r"^\d{4}:\d{2}:\d{2}\s+\d{2}:\d{2}:\d{2}$", ln):
                metadata_datetime_str = ln
                break

        if metadata_datetime_str:
            # e.g. "2023:08:25 12:34:56"
            date_part, time_part = metadata_datetime_str.split(" ")
            if date_part != folder_exif_date:
                # Update metadata with the correct date, keep the same time
                new_datetime_str = f"{folder_exif_date} {time_part}"
                _update_exif_metadata(file_path, new_datetime_str)
        else:
            # If we can't parse any valid date/time from metadata, set a default time
            new_datetime_str = f"{folder_exif_date} 00:00:00"
            _update_exif_metadata(file_path, new_datetime_str)

    except subprocess.CalledProcessError as e:
        print(f"Error reading metadata for {file_path}: {e}")
        # If reading fails, assume no date; set to folder date + 00:00:00
        new_datetime_str = f"{folder_exif_date} 00:00:00"
        _update_exif_metadata(file_path, new_datetime_str)

    # 2) Adjust the OS-level file times (and creation date if on macOS).
    #    We'll re-read the final date/time from the file’s metadata, then use that to set OS file timestamps.
    try:
        final_result = subprocess.run(
            ["exiftool", "-s3", "-DateTimeOriginal", "-CreateDate", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        lines = final_result.stdout.strip().splitlines()

        metadata_datetime_str = None
        for ln in lines:
            ln = ln.strip()
            if re.match(r"^\d{4}:\d{2}:\d{2}\s+\d{2}:\d{2}:\d{2}$", ln):
                metadata_datetime_str = ln
                break

        if metadata_datetime_str:
            dt = datetime.strptime(metadata_datetime_str, "%Y:%m:%d %H:%M:%S")
            _update_filesystem_times(file_path, dt)
    except subprocess.CalledProcessError as e:
        print(f"Error reading final metadata for OS-level timestamp update {file_path}: {e}")


def _update_exif_metadata(file_path, new_datetime_str):
    """
    Update the file's EXIF metadata date fields using exiftool.
    Example new_datetime_str: '2023:08:25 12:34:56'
    """
    try:
        subprocess.run(
            [
                "exiftool",
                "-overwrite_original",
                f"-DateTimeOriginal={new_datetime_str}",
                f"-CreateDate={new_datetime_str}",
                f"-ModifyDate={new_datetime_str}",
                file_path
            ],
            check=True
        )
        print(f"Updated metadata timestamps for {file_path} => {new_datetime_str}")
    except subprocess.CalledProcessError as e:
        print(f"Error updating EXIF metadata for {file_path}: {e}")

def _update_filesystem_times(file_path, dt):
    """
    Update the OS-level file timestamps. On macOS, we also set the 'creation date' via SetFile.
    If not on macOS or 'SetFile' is unavailable, you can remove/comment out those subprocess calls.
    """
    try:
        # For standard POSIX (atime, mtime), use os.utime:
        mod_time = dt.timestamp()
        os.utime(file_path, (mod_time, mod_time))

        # On macOS, we can update the 'creation date' using SetFile.
        dt_str_for_setfile = dt.strftime("%m/%d/%Y %H:%M:%S")  # e.g. "08/25/2023 12:34:56"
        subprocess.run(["SetFile", "-d", dt_str_for_setfile, file_path], check=True)
        subprocess.run(["SetFile", "-m", dt_str_for_setfile, file_path], check=True)
        print(f"OS-level creation/modified date updated (macOS) for {file_path} => {dt_str_for_setfile}")

    except FileNotFoundError:
        # 'SetFile' not found or not on macOS
        pass
    except subprocess.CalledProcessError as e:
        print(f"Error updating macOS creation date for {file_path}: {e}")

if __name__ == "__main__":
    input_directory = "/Volumes/SlowDisk/failed"
    output_directory = "/Volumes/G-DRIVE/Converted"
    processed_directory = "/Volumes/SlowDisk/iCloudBackup"
    target_bitrate = "8000k"

    process_media_files(input_directory, output_directory, processed_directory, target_bitrate)
