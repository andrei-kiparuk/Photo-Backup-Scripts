import os
import subprocess

# Define the list of photo and video file extensions
file_extensions = [
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.heic', '.heif', '.webp', '.jp2', '.exr', '.hdr',
    '.cr2', '.nef', '.arw', '.dng',
    '.mp4', '.mov', '.m4v', '.avi', '.wmv', '.flv', '.mkv', '.webm', '.3gp', '.mpeg', '.mpg', '.mts', '.m2ts', '.vob'
]

source_folder = "/Volumes/G-DRIVE/Converted"

for root, dirs, files in os.walk(source_folder):
    for file in files:
        if file.lower().endswith(tuple(file_extensions)):
            file_path = os.path.join(root, file)
            # Attempt to import into Photos app using osxphotos
            result = subprocess.run(['osxphotos', 'import', file_path, '--skip-dups', '--exiftool', '--verbose'], 
                                   capture_output=True, text=True)
            if result.returncode == 0 and "Imported" in result.stdout:
                try:
                    os.remove(file_path)
                    print(f"imported and deleted: {file_path}")
                except OSError as e:
                    print(f"Failed to delete {file_path}: {e}")
            elif result.returncode == 0:
                print(f"File {file} was not imported (possibly skipped), keeping it.")
            else:
                print(f"Failed to import {file}: {result.stderr}")