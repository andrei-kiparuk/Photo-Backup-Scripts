import os
import shutil
import subprocess

def import_photos_to_icloud(base_folder, destination_folder):
    """
    Traverse a base folder and subfolders, import photos into iCloud Photo Library,
    and move successfully imported files to a destination folder while preserving
    the original folder structure.
    
    Parameters:
        base_folder (str): Path to the base folder containing photos and videos.
        destination_folder (str): Path to the folder where imported files will be moved.
    """
    # Ensure the base folder exists
    if not os.path.exists(base_folder):
        raise FileNotFoundError(f"The folder '{base_folder}' does not exist.")
    
    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # Create the folder if it doesn't exist
    
    # Define supported file extensions for photos and videos
    supported_extensions = ('.jpg', '.jpeg', '.heic', '.dng', '.cr2', '.mov', '.mp4', '.avi')

    # Traverse the base folder and its subdirectories
    for root, _, files in os.walk(base_folder):
        for file in files:
            # Skip macOS resource fork files
            if file.startswith("._"):
                print(f"Skipping macOS resource file: {file}")
                continue
            
            # Process supported files
            if file.lower().endswith(supported_extensions):
                file_path = os.path.join(root, file)
                print(f"Found file: {file_path}")
                
                try:
                    print(f"Running command: osxphotos import {file_path}")
                    result = subprocess.run(
                        ["osxphotos", "import", file_path],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    print(f"STDOUT: {result.stdout}")
                    
                    # Determine relative path and create the same structure in destination
                    relative_path = os.path.relpath(file_path, base_folder)
                    dest_path = os.path.join(destination_folder, relative_path)
                    dest_dir = os.path.dirname(dest_path)
                    
                    # Ensure the destination subdirectory exists
                    if not os.path.exists(dest_dir):
                        os.makedirs(dest_dir)
                    
                    # Move the file to the destination, preserving folder structure
                    shutil.move(file_path, dest_path)
                    print(f"Moved file to {dest_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to import {file_path}: {e.stderr}")

if __name__ == "__main__":
    base_folder_path = "/Volumes/SlowDisk/iCloudbackup"
    destination_folder_path = "/Volumes/SlowDisk/PhotosImported"
    
    try:
        import_photos_to_icloud(base_folder_path, destination_folder_path)
    except Exception as e:
        print(f"Error: {e}")
