import os
import shutil
from datetime import datetime

def sort_files_by_date(source_dir, target_dir):
    """
    Sort files from the source directory (including its subfolders) into the target directory
    following the subfolders structure YYYY/MM/DD based on each file's creation date.
    """
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created target directory '{target_dir}'.")

    # Walk through the source directory and its subfolders
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                # Get the file's creation or modification date
                timestamp = os.path.getmtime(file_path)
                date = datetime.fromtimestamp(timestamp)
                year, month, day = date.strftime("%Y"), date.strftime("%m"), date.strftime("%d")

                # Create the destination folder structure YYYY/MM/DD
                dest_folder = os.path.join(target_dir, year, month, day)
                os.makedirs(dest_folder, exist_ok=True)

                # Move the file to the destination folder
                dest_path = os.path.join(dest_folder, file)
                shutil.move(file_path, dest_path)
                print(f"Moved '{file_path}' to '{dest_path}'.")

            except Exception as e:
                print(f"Error processing '{file_path}': {e}")

if __name__ == "__main__":
    # User-defined source and target directories
    source_directory = "path/to/source_directory"
    target_directory = "path/to/target_directory"

    sort_files_by_date(source_directory, target_directory)
