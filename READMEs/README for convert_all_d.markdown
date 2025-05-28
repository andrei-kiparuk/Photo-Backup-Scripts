# Convert All D Script

## Description
This Python script converts photos and videos to HEIC and HEVC, with a focus on handling duplicate files by checking file hashes before conversion. It organizes files into `YYYY/MM/DD` folders and preserves metadata using `exiftool`.

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
python3 convert_all_d.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_all_d.py /Volumes/WDsmall/Icloud
```
Converts `photo.jpg` to HEIC, saves to `/Volumes/JBOD/Converted/2023/05/27/photo.heic`, and skips duplicates based on file hash.

## Notes
- **Duplicates**: Uses SHA-256 hashes to skip identical files.
- **Metadata**: Preserves EXIF data with `exiftool`.
- **Error Handling**: Logs failed conversions to console.
- **Backup**: Back up files before running.