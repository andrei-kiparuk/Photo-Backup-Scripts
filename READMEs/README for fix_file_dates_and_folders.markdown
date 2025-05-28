# Fix File Dates and Folders Script

## Description
This Python script adjusts file creation/modification dates to match their `YYYY/MM/DD` folder structure and reorganizes files into correct folders if dates mismatch. It targets specific photo and video extensions.

## Prerequisites
- **Operating System**: Any
- **Dependencies**: Python 3.6+ (no external libraries required)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Folder Structure**: Files in `YYYY/MM/DD` subfolders

## Usage
Run the script to fix dates and folders.

### Command
```bash
python3 fix_file_dates_and_folders.py
```

### Parameters
- None (hardcoded base path)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 fix_file_dates_and_folders.py
```
Moves `photo.jpg` from `/Volumes/T7/to import/2023/05/27` to `/Volumes/T7/to import/2023/05/28` if EXIF date is `2023-05-28`.

## Notes
- **Folder Structure**: Enforces `YYYY/MM/DD` organization.
- **Backup**: Back up files before running.
- **Error Handling**: Logs invalid dates or inaccessible files.