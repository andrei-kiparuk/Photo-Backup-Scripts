# Apply Metadata Script

## Description
This Python script applies metadata from JSON files (e.g., from Google Takeout) to corresponding photo and video files in a specified folder. It uses `exiftool` to update EXIF data, ensuring creation dates and other metadata align with the JSON content.

## Prerequisites
- **Operating System**: Any (tested on macOS and Windows)
- **Dependencies**:
  - Python 3.6+
  - `exiftool`: Install via Homebrew (`brew install exiftool`) on macOS or download for Windows
- **Folder**: Source folder containing media files and `.json` metadata files
- **Permissions**: Read/write access to the source folder

## Usage
Run the script, specifying the source folder containing media and JSON files.

### Command
```bash
python3 apply_metadata.py /path/to/source
```

### Parameters
- `/path/to/source`: Path to the folder with media files and `.json` files

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.heif`, `.cr2`, `.dng`, `.tif`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`, `.3gp`

### Example
```bash
python3 apply_metadata.py /Volumes/T7/source
```
Applies metadata from `photo.jpg.json` to `photo.jpg`, updating EXIF data like creation date.

## Notes
- **JSON Format**: Expects Google Takeout-style JSON files with metadata (e.g., `photoTakenTime`).
- **Backup**: Back up files before running, as metadata changes are permanent.
- **Error Handling**: Skips files without corresponding JSON or invalid metadata; logs errors to console.
- **Dependencies**: Ensure `exiftool` is in your system PATH.