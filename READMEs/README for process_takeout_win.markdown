# Process Takeout Win Script

## Description
This Python script processes Google Takeout media files on Windows, applying JSON metadata to set correct dates and organizing files into `YYYY/MM/DD` folders. It converts files to HEIC/HEVC and uses `exiftool` for metadata.

## Prerequisites
- **Operating System**: Windows
- **Dependencies**:
  - Python 3.6+
  - `pillow`, `pillow_heif`: Install via `pip install pillow pillow_heif`
  - `ffmpeg`: Download and add to PATH
  - `exiftool`: Download and add to PATH
- **Folders**:
  - Source: `D:\Icloud` (read access)
  - Converted: `D:\Converted` (write access)
  - Processed: `D:\Processed` (write access)
- **Permissions**: Read/write access to all folders

## Usage
Run the script, specifying the source folder with Google Takeout files.

### Command
```bash
python process_takeout_win.py D:\Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media and JSON files (default: `D:\Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python process_takeout_win.py D:\Icloud
```
Converts `photo.jpg` to HEIC, uses `photo.jpg.json`, and saves to `D:\Converted\2023\05\27\photo.heic`.

## Notes
- **Google Takeout**: Expects JSON metadata files.
- **Backup**: Back up files before running.
- **Windows Paths**: Uses backslashes (`\`).