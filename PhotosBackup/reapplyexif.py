import os
import subprocess

# Define video and image extensions
video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".webm", ".3gp")
image_extensions = (".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif", ".cr2", ".dng")

def copy_exif_data(source_file, target_file):
    """Copy Exif data from source file to target file using ExifTool, with overwrite option."""
    command = ["exiftool", "-overwrite_original", "-tagsFromFile", source_file, target_file]
    subprocess.run(command)


def find_files_in_directory(directory):
    """Recursively find all files in a directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            yield os.path.join(root, file)

def get_converted_file(source_file, input_directory, processed_directory):
    """Return the corresponding converted file in input_directory (HEIC for images, MP4 for videos)."""
    file_name, file_extension = os.path.splitext(os.path.basename(source_file))
    
    # For video files, map to MP4
    if file_extension.lower() in video_extensions:
        converted_file_name = f"{file_name}.mp4"
    
    # For image files, map to HEIC
    elif file_extension.lower() in image_extensions:
        converted_file_name = f"{file_name}.heic"
    
    else:
        return None  # Unsupported file type

    # Get the relative path of the file in the processed directory
    relative_path = os.path.relpath(source_file, start=processed_directory)
    
    # Construct the corresponding converted file path
    converted_file = os.path.join(input_directory, relative_path)

    # Update the file extension to match the converted format (HEIC for images, MP4 for videos)
    converted_file = os.path.splitext(converted_file)[0] + os.path.splitext(converted_file_name)[1]

    return converted_file

def main(processed_directory, input_directory):
    """Find corresponding files in processed_directory and copy Exif data to input_directory."""
    for processed_file in find_files_in_directory(processed_directory):
        converted_file = get_converted_file(processed_file, input_directory, processed_directory)

        if converted_file and os.path.exists(converted_file):
            print(f"Copying EXIF data from {processed_file} to {converted_file}")
            copy_exif_data(processed_file, converted_file)
        else:
            print(f"Warning: {converted_file} does not exist or file type is unsupported. Skipping.")

if __name__ == "__main__":
    processed_directory = "/Volumes/G-DRIVE/processed/"  # Your processed directory path
    input_directory = "/Volumes/SlowDisk/Converted/"  # Your input directory path
    main(processed_directory, input_directory)
