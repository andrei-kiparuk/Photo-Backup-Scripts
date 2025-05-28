# Apply Metadata Updated Script

## Description
An enhanced version of `apply_metadata.py`, this Python script applies metadata from JSON files to media files, with improved date parsing (handling sub-second precision) and fallback to folder dates if JSON is missing. It uses `exiftool` to update EXIF data and supports a broader range of file extensions.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**:
  - Python 3.6+
  - `exiftool`: Install via Homebrew (`brew install exiftool`) on macOS
- **Folder**: Source folder with media files, `.json` files, and `YYYY/MM/DD` structure
- **Permissions**: Read/write access to the source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 apply_metadata_updated.py /path/to/source
```

### Parameters
- `/path/to/source`: Path to the folder with media files and `.json` files

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.heic`, `.heif`, `.cr2`, `.dng`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.m4v`, `.avi`, `.wmv`, `.flv`, `.mkv`, `.3gp`, `.mpeg`, `.vob`

### Example
```bash
python3 apply_metadata_updated.py /Volumes/T7/source
```
Applies metadata from `video.mp4.json` to `video.mp4` or uses folder date `2023/05/27` if JSON is missing.

## Notes
- **Date Parsing**: Handles sub-second precision (e.g., `2016:04:09 14:15:18.99`) by stripping sub-seconds.
- **Fallback**: Uses folder `YYYY/MM/DD` date if JSON metadata is unavailable.
- **Backup**: Back up files before running to prevent data loss.
- **Error Handling**: Logs invalid JSON or inaccessible files to console.