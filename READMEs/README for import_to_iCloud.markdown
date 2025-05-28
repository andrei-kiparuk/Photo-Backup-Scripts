# Import to iCloud Script

## Description
This Python script imports media files into the macOS Photos app with iCloud syncing enabled, using `osxphotos`. It organizes files into `YYYY/MM/DD` folders and moves imported files to a destination folder.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `osxphotos`: Install via `pip install osxphotos`
- **Folders**:
  - Source: `/Volumes/Converted` (read access)
  - Imported: `/Volumes/Imported` (write access)
- **Permissions**: Read/write access to folders; Photos app access
- **iCloud**: Active iCloud Photos sync

## Usage
Run the script to import media files.

### Command
```bash
python3 import_to_iCloud.py
```

### Parameters
- None (hardcoded source/destination paths)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 import_to_iCloud.py
```
Imports `photo.jpg` from `/Volumes/Converted/2023/05/27` to Photos app with iCloud sync and moves to `/Volumes/Imported/2023/05/27/photo.jpg`.

## Notes
- **iCloud**: Requires internet connection for syncing.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during import.