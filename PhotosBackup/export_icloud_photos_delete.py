import subprocess
import os
import sys
import datetime
import tempfile

# Define the export path on the external drive
EXPORT_PATH = "/Volumes/T7/Mac/"

# Temporary file to store UUIDs of exported photos
UUID_FILE = tempfile.NamedTemporaryFile(delete=False).name

# Command to export photos and videos using osxphotos
EXPORT_COMMAND = [
    "osxphotos",
    "export",
    EXPORT_PATH,
    "--export-by-date",
    "--use-photokit",
    "--update",
    "--download-missing",
    "--retry", "3",
    "--uuid",
    "--uuid-file", UUID_FILE,
    "--verbose"
]

# Command to delete photos by UUID using osxphotos
DELETE_COMMAND = [
    "osxphotos",
    "delete",
    "--uuid-from-file", UUID_FILE,
    "--yes"  # Confirm deletion without prompt
]

def log(message):
    """Log messages with timestamps."""
    print(f"{datetime.datetime.now()}: {message}")

def export_photos():
    """Run the osxphotos export command."""
    try:
        log("Starting export process...")
        subprocess.run(EXPORT_COMMAND, check=True)
        log(f"Photos and videos successfully exported to: {EXPORT_PATH}")
    except subprocess.CalledProcessError as e:
        log(f"Error during export: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log("Export interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log(f"An unexpected error occurred during export: {e}")
        sys.exit(1)

def delete_exported_photos():
    """Delete the exported photos from the iCloud Photos Library using UUIDs."""
    try:
        log("Starting deletion of exported photos from iCloud Photos Library...")
        subprocess.run(DELETE_COMMAND, check=True)
        log("Exported photos deleted successfully from the iCloud Photos Library.")
    except subprocess.CalledProcessError as e:
        log(f"Error during deletion: {e}")
        sys.exit(1)
    except Exception as e:
        log(f"An unexpected error occurred during deletion: {e}")
        sys.exit(1)
    finally:
        # Clean up the temporary UUID file
        if os.path.exists(UUID_FILE):
            os.remove(UUID_FILE)

def main():
    export_photos()
    delete_exported_photos()

if __name__ == "__main__":
    main()
