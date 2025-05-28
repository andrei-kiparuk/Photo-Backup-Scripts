# Convert All Fix Script

## Description
This Python script converts media files to HEIC and HEVC, fixing corrupted metadata during conversion. It uses `exiftool` to repair or reapply EXIF data and organizes files into `YYYY/MM/DD` folders based on corrected dates.

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
Run the script, specifying the source folder.

### Command
```bash
python3 convert_all_fix.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_all_fix.py /Volumes/WDsmall/Icloud
```
Converts `photo.jpg` to HEIC, fixes corrupted EXIF, and saves to `/Volumes/JBOD/Converted/2023/05/27/photo.heic`.

## Notes
- **Metadata Repair**: Attempts to restore missing or corrupted EXIF data.
- **Logging**: Logs repair attempts to console.
- **Backup**: Back up files before running to prevent data loss.