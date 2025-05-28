import subprocess
import os
import sys
import datetime

# Define the export path on the external drive
EXPORT_PATH = "/Volumes/SlowDisk/Mac"

# Command to export photos and videos using osxphotos
# -o: Output directory
# --export-by-date: Organize by date using structure YYYY/MM/DD
# --use-photokit: Use PhotoKit to access original files
# --update: Only export new or changed photos/videos if re-running the script
# --download-missing: Download missing originals from iCloud during export
# --retry 3: Retry failed exports up to 3 times
# --skip-missing: Skip photos with missing original files
# --verbose: Show detailed output during export

COMMAND = [
    "osxphotos",
    "export",
    EXPORT_PATH,
    "--export-by-date",
    "--use-photokit",
    "--update",  # Add this flag to ensure only new/changed photos are exported
    "--download-missing",
    "--retry", "3",
    "--filename", "{original_name}",
    "--verbose"
]

def log(message):
    """Log messages with timestamps."""
    print(f"{datetime.datetime.now()}: {message}")

def main():
    try:
        # Check if export path exists, create if not
        if not os.path.exists(EXPORT_PATH):
            os.makedirs(EXPORT_PATH)
            log(f"Created export directory: {EXPORT_PATH}")

        # Start the export process
        log("Starting export process...")
        subprocess.run(COMMAND, check=True)
        log(f"Photos and videos successfully exported to: {EXPORT_PATH}")

    except subprocess.CalledProcessError as e:
        log(f"Error during export: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log("Export interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
