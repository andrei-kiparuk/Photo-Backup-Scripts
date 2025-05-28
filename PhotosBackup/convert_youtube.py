import os
import shutil
import subprocess
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF support with Pillow
register_heif_opener()

def ensure_unique_filename(output_path):
    """
    Add a numeric suffix to the filename if it already exists to avoid overwrites.
    E.g., "image.heic" -> "image_1.heic", "image_2.heic", etc.
    """
    if not os.path.exists(output_path):
        return output_path

    base, ext = os.path.splitext(output_path)
    counter = 1
    new_output_path = f"{base}_{counter}{ext}"

    while os.path.exists(new_output_path):
        counter += 1
        new_output_path = f"{base}_{counter}{ext}"

    return new_output_path

def is_video_hevc(file_path):
    """
    Check if the video is encoded in HEVC (H.265) using ffprobe.
    Returns True if codec is hevc/h265, otherwise False.
    """
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
        print(f"Could not determine codec for {file_path}: {e}")
        return False

def copy_metadata(src, dst):
    """
    Copy metadata from src to dst using exiftool (if available).
    """
    try:
        subprocess.run(
            ["exiftool", "-overwrite_original", "-tagsFromFile", src, dst],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        print(f"Metadata copied from {src} to {dst}")
    except subprocess.CalledProcessError:
        print(f"ExifTool not available or error copying metadata from {src} to {dst}. Skipping...")

def convert_image_to_heic(input_path, output_path):
    """
    Convert an image to HEIC format while preserving metadata (if possible).
    """
    try:
        # Make sure we don't overwrite existing files
        output_path = ensure_unique_filename(output_path)

        # Convert with Pillow
        img = Image.open(input_path)
        img.save(output_path, format="HEIF")
        print(f"Converted image to HEIC: {output_path}")

        # Copy metadata (best effort)
        copy_metadata(input_path, output_path)

    except Exception as e:
        print(f"Error converting image {input_path}: {e}")

def convert_video_to_hevc(input_path, output_path, target_bitrate="8000k"):
    """
    Convert a video to HEVC (H.265) using ffmpeg.  
    Uses hardware-accelerated encoding on macOS (hevc_videotoolbox) if available.
    """
    try:
        output_path = ensure_unique_filename(output_path)
        print(f"Converting video to HEVC: {input_path} -> {output_path}")

        # Attempt hardware-accelerated encoding (macOS). If you need software fallback, adjust accordingly.
        subprocess.run(
            [
                "ffmpeg",
                "-i", input_path,
                "-c:v", "hevc_videotoolbox",
                "-b:v", target_bitrate,
                "-c:a", "aac",
                "-tag:v", "hvc1",
                output_path
            ],
            check=True
        )

        # Copy metadata (best effort)
        copy_metadata(input_path, output_path)
        print(f"Conversion complete: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error converting {input_path}: {e}")

def copy_file(src, dst):
    """
    Simply copy a file to the destination (used for files already in the desired format).
    """
    dst = ensure_unique_filename(dst)
    shutil.copy2(src, dst)
    print(f"Copied file (no conversion needed): {dst}")

def process_folder(input_folder, output_folder, target_bitrate="8000k"):
    """
    Scans through all files in 'input_folder', converts images to HEIC, videos to HEVC,
    and puts the results in 'output_folder'.
    """
    # Define extensions
    image_exts = {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif"}
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", ".3gp"}

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.startswith("._"):
            # Skip hidden macOS metadata files
            continue
        
        file_path = os.path.join(input_folder, filename)
        if not os.path.isfile(file_path):
            # Skip directories/subfolders
            continue

        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Handle images
        if ext in image_exts:
            heic_name = os.path.splitext(filename)[0] + ".heic"
            output_path = os.path.join(output_folder, heic_name)
            convert_image_to_heic(file_path, output_path)

        # Handle HEIC images (already in correct format)
        elif ext == ".heic":
            # Just copy it over
            output_path = os.path.join(output_folder, filename)
            copy_file(file_path, output_path)

        # Handle videos
        elif ext in video_exts:
            # Check if it's already HEVC
            if is_video_hevc(file_path):
                # Just copy if already H.265
                output_path = os.path.join(output_folder, filename)
                copy_file(file_path, output_path)
            else:
                # Convert to HEVC
                new_name = os.path.splitext(filename)[0] + "_hevc.mp4"
                output_path = os.path.join(output_folder, new_name)
                convert_video_to_hevc(file_path, output_path, target_bitrate)

        else:
            print(f"Skipping unsupported file type: {filename}")

if __name__ == "__main__":
    # Change these paths to match your setup
    input_dir = "/Volumes/G-DRIVE/YoutubeBackup/Downloaded/toconvert"
    output_dir = "/Volumes/G-DRIVE/YoutubeBackup/Downloaded/Converted"

    # Set your desired target bitrate (e.g., "8000k", "10000k", etc.)
    bitrate = "20000k"

    process_folder(input_dir, output_dir, bitrate)
