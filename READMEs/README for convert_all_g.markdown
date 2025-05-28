# Convert All G Script

## Description
This Python script converts media files to HEIC and HEVC, optimized for Google Takeout exports. It processes JSON metadata files to set correct dates and organizes files into `YYYY/MM/DD` folders, using `exiftool` for metadata preservation.

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
python3 convert_all_g.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media and JSON files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_all_g.py /Volumes/WDsmall/Icloud
```
Converts `photo.jpg` to HEIC, uses `photo.jpg.json` for metadata, and saves to `/Volumes/JBOD/Converted/2023/05/27/photo.heic`.

## Notes
- **Google Takeout**: Expects JSON metadata files (e.g., `photo.jpg.json`).
- **Metadata**: Applies dates and EXIF from JSON using `exiftool`.
- **Backup**: Back up files before running.