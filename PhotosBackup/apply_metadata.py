import os
import json
import subprocess
from datetime import datetime

# Folder path for unpacked Google Takeout
base_path = "/Volumes/RAID/unpack/Takeout/Google Photos"
failed_log_path = "failed_files.log"

# List of common EXIF, IPTC, and XMP tags to avoid unsupported tag warnings
supported_tags = {
    "DateTimeOriginal", "CreateDate", "ModifyDate", "Make", "Model", "Orientation",
    "GPSLatitude", "GPSLongitude", "Artist", "Copyright", "Description", "Keywords",
    "Title", "Subject", "Location"
}

# Function to log failed files
def log_failure(json_path, media_file_path=None, error=None):
    with open(failed_log_path, "a") as log_file:
        log_file.write(f"JSON: {json_path}, Media: {media_file_path}, Error: {error}\n")

# Function to set metadata and dates
def apply_metadata(file_path, metadata, json_path):
    try:
        # Prepare exiftool command
        exiftool_command = ["exiftool"]

        # Add only supported metadata fields to exiftool command
        for key, value in metadata.items():
            if isinstance(value, str) and key in supported_tags:
                exiftool_command.extend([f"-{key}={value}"])

        # Execute exiftool command to set metadata
        exiftool_command.append(file_path)
        subprocess.run(exiftool_command, check=True)

        # Set file creation and modification dates
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
                os.utime(file_path, (date_time_obj.timestamp(), date_time_obj.timestamp()))
            except Exception as e:
                log_failure(json_path, file_path, f"Invalid date format: {e}")
                return
        else:
            log_failure(json_path, file_path, "Missing both photoTakenTime and creationTime")
            return

        # Print the file name if metadata application is successful
        print(f"Processed file: {file_path}")

    except Exception as e:
        log_failure(json_path, file_path, f"Metadata application error: {e}")

# Function to find matching file
def find_matching_file(root, title):
    file_path = os.path.join(root, title)
    if os.path.exists(file_path):
        return file_path

    # Attempt case-insensitive match
    matched_files = [f for f in os.listdir(root) if f.lower() == title.lower()]
    if matched_files:
        return os.path.join(root, matched_files[0])

    return None

# Function to parse JSON metadata and apply it to files
def process_takeout_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".json"):
                json_path = os.path.join(root, file_name)
                try:
                    with open(json_path, "r") as json_file:
                        metadata = json.load(json_file)

                    # Locate corresponding photo or video file
                    title = metadata.get("title", "")
                    if isinstance(title, list):  # Handle cases where title is a list
                        title = title[0]
                    media_file_path = find_matching_file(root, title)

                    if media_file_path:
                        apply_metadata(media_file_path, metadata, json_path)
                    else:
                        log_failure(json_path, None, "Media file not found")

                except Exception as e:
                    log_failure(json_path, None, f"JSON processing error: {e}")

# Function to retry failed files
def retry_failed_files():
    if not os.path.exists(failed_log_path):
        print("No failed log file found.")
        return

    with open(failed_log_path, "r") as log_file:
        lines = log_file.readlines()

    # Clear the log file for next retry attempt
    open(failed_log_path, "w").close()

    for line in lines:
        try:
            parts = line.strip().split(", ")
            json_path = parts[0].split(": ", 1)[1]
            media_file_path = parts[1].split(": ", 1)[1] if "Media:" in parts[1] else None

            with open(json_path, "r") as json_file:
                metadata = json.load(json_file)

            if not media_file_path or not os.path.exists(media_file_path):
                title = metadata.get("title", "")
                if isinstance(title, list):
                    title = title[0]
                media_file_path = find_matching_file(os.path.dirname(json_path), title)

            if media_file_path:
                apply_metadata(media_file_path, metadata, json_path)
            else:
                log_failure(json_path, None, "Media file not found during retry")

        except Exception as e:
            log_failure(json_path, None, f"Retry error: {e}")

# Run the script
print("Processing Takeout folder...")
process_takeout_folder(base_path)
print("Processing complete.")

# Uncomment the line below to retry failed files
# print("Retrying failed files...")
# retry_failed_files()
# print("Retry complete.")
