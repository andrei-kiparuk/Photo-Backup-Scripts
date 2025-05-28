# Import OSX Script

## Description
This Python script imports media files into the macOS Photos app using `osxphotos`, organizing them into `YYYY/MM/DD` folders post-import. It preserves metadata and moves imported files to a destination folder.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `osxphotos`: Install via `pip install osxphotos`
- **Folders**:
  - Source: `/Volumes/Converted` (read access)
  - Imported: `/Volumes/Imported` (write access)
- **Permissions**: Read/write access to folders; Photos app access

## Usage
Run the script to import media files.

### Command
```bash
python3 import_osx.py
```

### Parameters
- None (hardcoded source/destination paths)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 import_osx.py
```
Imports `photo.jpg` from `/Volumes/Converted/2023/05/27` to Photos app and moves to `/Volumes/Imported/2023/05/27/photo.jpg`.

## Notes
- **Folder Structure**: Preserves `YYYY/MM/DD` hierarchy.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during import.