# Google Import Script

## Description
This Python script imports Google Takeout media files into the macOS Photos app using `osxphotos`, applying JSON metadata for correct dates. It organizes files into `YYYY/MM/DD` folders post-import.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `osxphotos`: Install via `pip install osxphotos`
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folders**:
  - Source: `/Volumes/WDsmall/Icloud` (read access)
  - Imported: `/Volumes/Imported` (write access)
- **Permissions**: Read/write access to folders; Photos app access

## Usage
Run the script, specifying the source folder with Google Takeout files.

### Command
```bash
python3 google_import.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media and JSON files

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 google_import.py /Volumes/WDsmall/Icloud
```
Imports `photo.jpg` to Photos app, using `photo.jpg.json` for metadata, and moves to `/Volumes/Imported/2023/05/27/photo.jpg`.

## Notes
- **Google Takeout**: Expects JSON metadata files.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during import.