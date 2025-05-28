# Reapply EXIF Script

## Description
This Python script reapplies EXIF metadata to media files using `exiftool`, correcting or restoring metadata from JSON files or existing EXIF data. It’s useful for fixing corrupted metadata before import.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**:
  - Python 3.6+
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 reapplyexif.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media and optional JSON files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 reapplyexif.py /Volumes/T7/to import
```
Reapplies EXIF to `photo.jpg` using `photo.jpg.json` or existing metadata.

## Notes
- **JSON Support**: Uses Google Takeout-style JSON if available.
- **Backup**: Back up files before running to prevent data loss.
- **Error Handling**: Logs invalid metadata to console.