# Convert Takeout Mac SlowDisk Script

## Description
A variant of `convert_takeout_mac.py`, this Python script converts Google Takeout media files to HEIC and HEVC, optimized for slower external drives. It reduces I/O operations, uses JSON metadata, and organizes files into `YYYY/MM/DD` folders.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `pillow`, `pillow_heif`: Install via `pip install pillow pillow_heif`
  - `ffmpeg`: Install via Homebrew (`brew install ffmpeg`)
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folders**:
  - Source: `/Volumes/WDsmall/Icloud` (read access)
  - Converted: `/Volumes/JBOD/Converted` (write access)
  - Processed: `/Volumes/WDsmall/Processed` (write access)
- **Permissions**: Read/write access to all folders

## Usage
Run the script, specifying the source folder with Google Takeout files.

### Command
```bash
python3 convert_takeout_mac_SlowDisk.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media and JSON files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_takeout_mac_SlowDisk.py /Volumes/WDsmall/Icloud
```
Converts `photo.jpg` to HEIC, uses `photo.jpg.json`, and saves to `/Volumes/JBOD/Converted/2023/05/27/photo.heic`.

## Notes
- **Slow Drives**: Minimizes disk I/O for better performance on slower drives.
- **Google Takeout**: Expects JSON metadata files.
- **Backup**: Back up files before running.