import os
import shutil
import subprocess
import platform
import logging
import argparse
from PIL import Image
from pillow_heif import register_heif_opener
from datetime import datetime
import re
import concurrent.futures
from tqdm import tqdm
import time
import sys
import hashlib

# Register HEIF support with Pillow
register_heif_opener()

# Directory configuration
INPUT_DIRECTORY = "/Volumes/SlowDisk/icloud"
OUTPUT_DIRECTORY = "/Volumes/G-DRIVE/Converted"
PROCESSED_DIRECTORY = "/Volumes/G-DRIVE/ProcessedOriginals"
FAILED_DIRECTORY = "/Volumes/G-DRIVE/FailedImports"
LOG_FILE = "media_conversion.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global counters
PHOTOS_RESTART_COUNT = 0
MAX_PHOTOS_RESTARTS = 100
SUCCESSFUL_IMPORT_COUNT = 0
FAILED_IMPORT_COUNT = 0
OSASCRIPT_IMPORT_COUNT = 0
IMPORTS_PER_RESTART = 1500
SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE = 0

def check_dependencies():
    """Check if required external tools are installed."""
    dependencies = ["osxphotos", "exiftool", "ffmpeg", "ffprobe"]
    missing = []
    for dep in dependencies:
        if not shutil.which(dep):
            missing.append(dep)
    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        sys.exit(1)
    logger.info(f" ")    
    logger.info("All dependencies are installed.")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Convert and organize media files.")
    parser.add_argument("--quality", type=int, default=90, choices=range(0, 101),
                        help="Video conversion quality percentage (0-100, default: 90)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate actions without modifying files")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel workers (default: 4)")
    return parser.parse_args()

def ensure_unique_filename(output_path, dry_run=False):
    """Add a numeric suffix to the filename if it already exists."""
    if dry_run or not os.path.exists(output_path):
        return output_path
    base, ext = os.path.splitext(output_path)
    counter = 1
    new_output_path = f"{base}_{counter}{ext}"
    while os.path.exists(new_output_path):
        counter += 1
        new_output_path = f"{base}_{counter}{ext}"
    return new_output_path

def compute_file_hash(file_path):
    """Compute SHA-256 hash of a file's contents."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to compute hash for {file_path}: {e}")
        return None

def check_for_duplicates(file_path, library_path, dry_run=False):
    """Check if a file is a duplicate in the Photos library by comparing hashes."""
    if dry_run:
        return False
    file_hash = compute_file_hash(file_path)
    if not file_hash:
        return False
    # Assume Photos library stores originals in ~/Pictures/Photos Library.photoslibrary/originals
    originals_path = os.path.join(library_path, "originals")
    if not os.path.exists(originals_path):
        logger.warning(f"Photos library originals path not found: {originals_path}")
        return False
    for root, _, files in os.walk(originals_path):
        for fname in files:
            library_file = os.path.join(root, fname)
            library_hash = compute_file_hash(library_file)
            if library_hash and library_hash == file_hash:
                logger.info(f"Duplicate found: {file_path} matches {library_file}")
                return True
    return False

def extract_dates_from_metadata(file_path, dry_run=False):
    """Extract possible dates from metadata using ExifTool."""
    if dry_run:
        return []
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
        logger.error(f"Error extracting metadata dates from {file_path}: {e}")
        return []

def validate_metadata(file_path, dry_run=False):
    """Validate that the file has required EXIF metadata for import."""
    if dry_run:
        return True
    try:
        result = subprocess.run(
            ["exiftool", "-s", "-s", "-s", "-DateTimeOriginal", "-CreateDate", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return bool(result.stdout.strip())  # True if any metadata is present
    except Exception as e:
        logger.warning(f"No valid metadata found for {file_path}: {e}")
        return False

def validate_file_integrity(file_path, dry_run=False):
    """Validate that the file is a valid image or video."""
    if dry_run:
        return True
    try:
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.cr2', '.dng', '.heic')):
            Image.open(file_path).verify()  # Verify image integrity
        elif file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.mpeg', '.webm', '.3gp')):
            # Basic FFmpeg check for video integrity
            subprocess.run(
                ["ffmpeg", "-v", "error", "-i", file_path, "-f", "null", "-"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
            )
        return True
    except Exception as e:
        logger.warning(f"File integrity check failed for {file_path}: {e}")
        return False

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

def get_oldest_date(file_path, dry_run=False):
    """Get the oldest date from metadata, path, or file modification time."""
    metadata_dates = extract_dates_from_metadata(file_path, dry_run)
    path_date = extract_date_from_path(file_path)
    all_dates = metadata_dates + ([path_date] if path_date else [])
    if all_dates:
        return min(all_dates).strftime("%Y/%m/%d")
    if dry_run:
        return datetime.now().strftime("%Y/%m/%d")
    return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y/%m/%d")

def preserve_timestamps(src, dest, dry_run=False):
    """Preserve the original file's creation and modification timestamps."""
    if dry_run:
        logger.info(f" ")
        logger.info(f"[Dry Run] Would preserve timestamps for {dest}")
        return
    try:
        stat = os.stat(src)
        os.utime(dest, (stat.st_atime, stat.st_mtime))
        logger.info(f" ")
        logger.info(f"Preserved timestamps for {dest}")
    except Exception as e:
        logger.error(f"Error preserving timestamps for {dest}: {e}")

def move_to_processed(src, processed_root, dry_run=False):
    """Move the source file to the processed folder organized by date."""
    try:
        date_folder = get_oldest_date(src, dry_run)
        processed_folder = os.path.join(processed_root, date_folder)
        if not dry_run:
            os.makedirs(processed_folder, exist_ok=True)
        destination_path = ensure_unique_filename(os.path.join(processed_folder, os.path.basename(src)), dry_run)
        if dry_run:
            logger.info(f" ")
            logger.info(f"[Dry Run] Would move {src} to {destination_path}")
        else:
            shutil.move(src, destination_path)
            logger.info(f" ")
            logger.info(f"Moved original to: {destination_path}")
    except Exception as e:
        logger.error(f"Error moving file {src} to processed folder: {e}")

def move_to_failed(src, failed_root, dry_run=False):
    """Move the source file to the failed imports folder organized by date."""
    try:
        date_folder = get_oldest_date(src, dry_run)
        failed_folder = os.path.join(failed_root, date_folder)
        if not dry_run:
            os.makedirs(failed_folder, exist_ok=True)
        destination_path = ensure_unique_filename(os.path.join(failed_folder, os.path.basename(src)), dry_run)
        if dry_run:
            logger.info(f" ")
            logger.info(f"[Dry Run] Would move failed import {src} to {destination_path}")
        else:
            shutil.move(src, destination_path)
            logger.info(f" ")
            logger.info(f"Moved failed import to: {destination_path}")
    except Exception as e:
        logger.error(f"Error moving failed import {src} to failed folder: {e}")

def restart_photos_app(dry_run=False):
    """Restart the Photos app on macOS."""
    global PHOTOS_RESTART_COUNT, SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE
    if dry_run:
        logger.info(f" ")
        logger.info("[Dry Run] Would restart Photos app")
        return
    if PHOTOS_RESTART_COUNT >= MAX_PHOTOS_RESTARTS:
        logger.warning(f" ")
        logger.warning(f"Maximum Photos app restarts ({MAX_PHOTOS_RESTARTS}) reached. Skipping restart.")
        return
    try:
        # Check if Photos app is running
        check_result = subprocess.run(
            ["ps", "-ax", "-o", "comm"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        if "Photos.app" not in check_result.stdout:
            logger.info(f" ")
            logger.info("Photos app is not running. Starting Photos app.")
        else:
            # Try to quit Photos app gracefully
            try:
                subprocess.run(
                    ["osascript", "-e", 'tell application "Photos" to quit'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                )
                logger.info(f" ")
                logger.info("Closed Photos app via osascript")
            except subprocess.CalledProcessError:
                # Fallback to killall
                subprocess.run(
                    ["killall", "Photos"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
                )
                logger.info(f" ")
                logger.info("Closed Photos app via killall")
            # Wait to ensure the app is fully closed
            time.sleep(2)
        # Reopen Photos app
        subprocess.run(
            ["open", "-a", "Photos"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        logger.info(f" ")
        logger.info("Reopened Photos app")
        # Wait for the app to stabilize
        time.sleep(5)
        PHOTOS_RESTART_COUNT += 1
        logger.info(f" ")
        logger.info(f"Photos app restart count: {PHOTOS_RESTART_COUNT}/{MAX_PHOTOS_RESTARTS}")
        # Reset restart count if many successful imports since last failure
        if SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE > 3000:
            PHOTOS_RESTART_COUNT = 0
            logger.info(f" ")
            logger.info("Reset Photos app restart count due to 3000+ successful imports without failures")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error restarting Photos app: {e.stderr.strip()}")
    except Exception as e:
        logger.error(f"Unexpected error restarting Photos app: {e}")

def import_with_osascript(file_path, dry_run=False):
    """Import a file into Photos app using osascript."""
    global OSASCRIPT_IMPORT_COUNT
    if dry_run:
        logger.info(f" ")
        logger.info(f"[Dry Run] Would import {file_path} with osascript")
        return True
    try:
        script = f'''
        tell application "Photos"
            activate
            import POSIX file "{file_path}"
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        logger.info(f" ")
        logger.info(f"Successfully imported {file_path} with osascript")
        OSASCRIPT_IMPORT_COUNT += 1
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to import {file_path} with osascript: {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error importing {file_path} with osascript: {e}")
        return False

def retry_operation(operation, *args, max_attempts=3, base_delay=1, dry_run=False, **kwargs):
    """Retry an operation with manual error checking for osxphotos import."""
    for attempt in range(max_attempts):
        try:
            result = operation(*args, **kwargs)
            # Check osxphotos import output for errors
            if args and args[0][0] == "osxphotos" and args[0][1] == "import":
                combined_output = result.stdout + result.stderr
                if "Error importing file" in combined_output or "imported 0 file groups" in combined_output:
                    raise subprocess.CalledProcessError(1, args[0], output=combined_output, stderr=result.stderr)
            return result
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            # For osxphotos import, restart Photos app after second failure
            if attempt == 1 and args and args[0][0] == "osxphotos" and args[0][1] == "import":
                logger.info(f" ")
                logger.info(f"Triggering Photos app restart after attempt {attempt + 1} failed for {args[0][-1]}")
                restart_photos_app(dry_run)
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)

def convert_image_to_heic(input_path, output_path, dry_run=False):
    """Convert an image to HEIC format while preserving metadata."""
    try:
        output_path = ensure_unique_filename(output_path, dry_run)
        if dry_run:
            logger.info(f" ")
            logger.info(f"[Dry Run] Would convert {input_path} to {output_path}")
            return output_path
        image = Image.open(input_path)
        image.save(output_path, format="HEIF")
        result = retry_operation(
            subprocess.run,
            ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        logger.info(f" ")
        logger.info(f"Image converted: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting image {input_path}: {e}")
        if not dry_run and os.path.exists(output_path):
            logger.info(f"Cleaning up failed output file: {output_path}")
            os.remove(output_path)
        raise

def convert_video_to_hevc(input_path, output_path, quality=90, dry_run=False):
    """Convert a video to HEVC using appropriate encoder based on platform."""
    try:
        output_path = ensure_unique_filename(output_path, dry_run)
        is_macos = platform.system() == "Darwin"
        if is_macos:
            # macOS: Use hevc_videotoolbox with quality mapped to 0-100
            ffmpeg_args = [
                "ffmpeg", "-i", input_path, "-c:v", "hevc_videotoolbox",
                "-q:v", str(quality), "-c:a", "aac", "-tag:v", "hvc1", output_path
            ]
        else:
            # Other platforms: Use libx265 with CRF (0-51, reversed quality)
            crf = int((100 - quality) * 51 / 100)  # Map 100->0, 0->51
            ffmpeg_args = [
                "ffmpeg", "-i", input_path, "-c:v", "libx265",
                "-crf", str(crf), "-preset", "medium", "-c:a", "aac", "-tag:v", "hvc1", output_path
            ]
        if dry_run:
            logger.info(f" ")
            logger.info(f"[Dry Run] Would convert {input_path} to {output_path} with args: {' '.join(ffmpeg_args)}")
            return output_path
        retry_operation(subprocess.run, ffmpeg_args, check=True)
        retry_operation(
            subprocess.run,
            ["exiftool", "-overwrite_original", "-tagsFromFile", input_path, output_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        logger.info(f" ")
        logger.info(f"Video converted: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error converting video {input_path}: {e}")
        if not dry_run and os.path.exists(output_path):
            logger.info(f"Cleaning up failed output file: {output_path}")
            os.remove(output_path)
        raise

def is_video_hevc(file_path, dry_run=False):
    """Check if the video is encoded in HEVC."""
    if dry_run:
        return False
    try:
        result = retry_operation(
            subprocess.run,
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name",
             "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        codec = result.stdout.strip().lower()
        return codec in ["hevc", "h265"]
    except Exception:
        return False

def copy_file_to_output(input_path, output_path, dry_run=False):
    """Copy file to output directory and preserve timestamps."""
    output_path = ensure_unique_filename(output_path, dry_run)
    logger.info(f" ")
    logger.info(f"Source: {input_path}")
    if dry_run:
        logger.info(f" ")
        logger.info(f"[Dry Run] Would copy {input_path} to {output_path}")
        return output_path
    shutil.copy2(input_path, output_path)
    logger.info(f" ")
    logger.info(f"Copied to: {output_path}")
    return output_path

def process_file(file_info, input_dir, output_dir, processed_dir, failed_dir, quality, dry_run):
    """Process a single media file."""
    global SUCCESSFUL_IMPORT_COUNT, FAILED_IMPORT_COUNT, SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE
    root, file = file_info
    file_path = os.path.join(root, file)
    try:
        if file.startswith("._") or file == ".DS_Store":
            logger.info(f" ")
            logger.info(f"Skipping system file: {file}")
            return
        if not os.path.isfile(file_path):
            return

        _, ext = os.path.splitext(file)
        video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", ".3gp")
        image_extensions = (".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".cr2", ".dng", ".heic")

        # Skip unsupported extensions early
        if ext.lower() not in video_extensions + image_extensions:
            logger.info(f" ")
            logger.info(f"Skipping unsupported file: {file_path}")
            return

        # Validate metadata and file integrity before processing
        if not validate_metadata(file_path, dry_run):
            logger.info(f" ")
            logger.info(f"Skipping file with invalid metadata: {file_path}")
            if not dry_run:
                move_to_failed(file_path, failed_dir, dry_run)
                FAILED_IMPORT_COUNT += 1
            return
        if not validate_file_integrity(file_path, dry_run):
            logger.info(f" ")
            logger.info(f"Skipping file with invalid integrity: {file_path}")
            if not dry_run:
                move_to_failed(file_path, failed_dir, dry_run)
                FAILED_IMPORT_COUNT += 1
            return

        # Check for duplicates in Photos library
        library_path = os.path.expanduser("~/Pictures/Photos Library.photoslibrary")
        if check_for_duplicates(file_path, library_path, dry_run):
            logger.info(f" ")
            logger.info(f"Skipping duplicate file: {file_path}")
            if not dry_run:
                move_to_failed(file_path, failed_dir, dry_run)
                FAILED_IMPORT_COUNT += 1
            return

        date_folder = get_oldest_date(file_path, dry_run)
        output_folder = os.path.join(output_dir, date_folder)
        if not dry_run:
            os.makedirs(output_folder, exist_ok=True)

        if ext.lower() == ".heic":
            output_file = os.path.join(output_folder, file)
            output_file = copy_file_to_output(file_path, output_file, dry_run)
        elif ext.lower() in image_extensions:
            output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}.heic")
            output_file = convert_image_to_heic(file_path, output_file, dry_run)
            if not dry_run:
                preserve_timestamps(file_path, output_file, dry_run)
        elif ext.lower() in video_extensions:
            if is_video_hevc(file_path, dry_run):
                output_file = os.path.join(output_folder, file)
                output_file = copy_file_to_output(file_path, output_file, dry_run)
            else:
                output_file = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_hevc.mp4")
                output_file = convert_video_to_hevc(file_path, output_file, quality, dry_run)
                if not dry_run:
                    preserve_timestamps(file_path, output_file, dry_run)

        if not dry_run:
            move_to_processed(file_path, processed_dir, dry_run)
            # Try osxphotos import with skip-duplicates
            try:
                import_result = retry_operation(
                    subprocess.run,
                    ["osxphotos", "import", "--verbose", "--skip-duplicates", output_file],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, dry_run=dry_run
                )
                combined_output = import_result.stdout + import_result.stderr
                if "Error importing file" not in combined_output and "imported 0 file groups" not in combined_output:
                    logger.info(f" ")
                    logger.info(f"Processed and imported: {output_file}")
                    SUCCESSFUL_IMPORT_COUNT += 1
                    SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE += 1
                    # Restart Photos app every 1500 successful imports
                    if SUCCESSFUL_IMPORT_COUNT % IMPORTS_PER_RESTART == 0:
                        logger.info(f" ")
                        logger.info(f"Reached {SUCCESSFUL_IMPORT_COUNT} successful imports. Triggering Photos app restart.")
                        restart_photos_app(dry_run)
                    return
                else:
                    logger.error(f"Failed to import {output_file} with osxphotos: {import_result.stderr.strip() or combined_output.strip()}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to import {output_file} with osxphotos: {e.stderr.strip() or e.output.strip()}")
            
            # Reset successful imports since last failure
            SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE = 0
            # Fallback to osascript import
            logger.info(f" ")
            logger.info(f"Attempting to import {output_file} with osascript")
            if import_with_osascript(output_file, dry_run):
                SUCCESSFUL_IMPORT_COUNT += 1
                SUCCESSFUL_IMPORTS_SINCE_LAST_FAILURE += 1
                # Restart Photos app every 1500 successful imports
                if SUCCESSFUL_IMPORT_COUNT % IMPORTS_PER_RESTART == 0:
                    logger.info(f" ")
                    logger.info(f"Reached {SUCCESSFUL_IMPORT_COUNT} successful imports. Triggering Photos app restart.")
                    restart_photos_app(dry_run)
            else:
                logger.error(f"Failed to import {output_file} with both osxphotos and osascript")
                logger.warning(f"Duplicate dialog may appear for {output_file}. Consider manual import or third-party tools like PowerPhotos.")
                move_to_failed(output_file, failed_dir, dry_run)
                FAILED_IMPORT_COUNT += 1
        else:
            logger.info(f" ")
            logger.info(f"[Dry Run] Would process and import: {output_file}")

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

def process_media_files(input_dir, output_dir, processed_dir, failed_dir, quality=90, dry_run=False, workers=4):
    """Process media files in parallel with progress reporting."""
    global SUCCESSFUL_IMPORT_COUNT, FAILED_IMPORT_COUNT, OSASCRIPT_IMPORT_COUNT
    logger.info(f"Starting media processing (Quality: {quality}%, Dry Run: {dry_run}, Workers: {workers})")
    
    # Collect all files
    files = []
    for root, _, filenames in sorted(os.walk(input_dir), key=lambda x: x[0], reverse=False):
        for file in sorted(filenames):
            files.append((root, file))
    
    # Process files in parallel with progress bar
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                process_file, (root, file), input_dir, output_dir, processed_dir, failed_dir, quality, dry_run
            )
            for root, file in files
        ]
        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing files"):
            pass
    
    logger.info(f" ")
    logger.info(f"Media processing completed. Successful imports: {SUCCESSFUL_IMPORT_COUNT} (osxphotos: {SUCCESSFUL_IMPORT_COUNT - OSASCRIPT_IMPORT_COUNT}, osascript: {OSASCRIPT_IMPORT_COUNT}), Failed imports: {FAILED_IMPORT_COUNT}, Photos app restarts: {PHOTOS_RESTART_COUNT}")

if __name__ == "__main__":
    check_dependencies()
    args = parse_arguments()
    process_media_files(
        INPUT_DIRECTORY,
        OUTPUT_DIRECTORY,
        PROCESSED_DIRECTORY,
        FAILED_DIRECTORY,
        quality=args.quality,
        dry_run=args.dry_run,
        workers=args.workers
    )