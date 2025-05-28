import os
import subprocess
import json
from pathlib import Path

# Define constants
EXPORT_DIR = "/Volumes/G-DRIVE/Mac"
EXPORTED_UUIDS_FILE = "/Volumes/G-DRIVE/Mac/exported_uuids.txt"  # File to track exported photo UUIDs

# Set DRY_RUN to True for testing without making changes
DRY_RUN = False  # Change to False to execute actual operations


def run_command(command, dry_run=False):
    """Run a shell command with optional dry run."""
    if dry_run:
        print(f"[DRY RUN] Command: {' '.join(command)}")
    else:
        subprocess.run(command, check=True)


# Ensure the export directory exists
Path(EXPORT_DIR).mkdir(parents=True, exist_ok=True)

# Step 1: Fetch all UUIDs using osxphotos query
QUERY_COMMAND = [
    "osxphotos",
    "query",
    "--json",  # Output all photo metadata as JSON
]

print("Fetching UUIDs of photos to export...")
if not DRY_RUN:
    result = subprocess.run(
        QUERY_COMMAND, stdout=subprocess.PIPE, check=True, text=True
    )
    # Parse JSON and extract UUIDs
    photo_data = json.loads(result.stdout)
    uuids = [photo["uuid"] for photo in photo_data]
    # Write UUIDs to file
    with open(EXPORTED_UUIDS_FILE, "w") as f:
        f.write("\n".join(uuids))

# Step 2: Export photos using the UUIDs file
EXPORT_COMMAND = [
    "osxphotos",
    "export",
    EXPORT_DIR,
    "--directory",
    "{created.year}/{created.mm}/{created.dd}",  # Subfolder structure
    "--overwrite",  # Overwrite existing files
    "--verbose",
    "--exiftool",
    "--download-missing",
    "--retry", "3",    
    "--update",  # Only export updated or new photos
    "--exportdb",
    f"{EXPORT_DIR}/osxphotos_export.db",  # Use export database for tracking
    "--uuid-from-file",
    EXPORTED_UUIDS_FILE,  # File containing UUIDs to export
]

print("Exporting photos...")
run_command(EXPORT_COMMAND, dry_run=DRY_RUN)

# Step 3: Delete only exported photos
if not DRY_RUN:
    with open(EXPORTED_UUIDS_FILE, "r") as f:
        uuids = [line.strip() for line in f if line.strip()]

    for uuid in uuids:
        DELETE_COMMAND = [
            "osxphotos",
            "delete",
            "--yes",  # Confirm deletion without prompt
            "--uuid",
            uuid,
        ]
        print(f"Deleting photo with UUID: {uuid}")
        run_command(DELETE_COMMAND, dry_run=DRY_RUN)

print("Dry run completed!" if DRY_RUN else "Export and selective deletion completed!")
