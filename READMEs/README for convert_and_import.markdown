# Convert and Import Script

## Description
This Python script converts media files to HEIC and HEVC, then imports them into the macOS Photos app using `osxphotos`. It organizes converted files into `YYYY/MM/DD` folders, preserves metadata with `exiftool`, and moves originals to a processed folder.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `pillow`, `pillow_heif`: Install via `pip install pillow pillow_heif`
  - `ffmpeg`: Install via Homebrew (`brew install ffmpeg`)
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
  - `osxphotos`: Install via `pip install osxphotos`
- **Folders**:
  - Source: `/Volumes/WDsmall/Icloud` (read access)
  - Converted: `/Volumes/JBOD/Converted` (write access)
  - Processed: `/Volumes/WDsmall/Processed` (write access)
- **Permissions**: Read/write access to all folders; Photos app access

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 convert_and_import.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_and_import.py /Volumes/WDsmall/Icloud
```
Converts `photo.jpg` to HEIC, imports to Photos app, and moves original to `/Volumes/WDsmall/Processed/2023/05/27/photo.jpg`.

## Notes
- **Photos App**: Ensure Photos app is not running during import.
- **Metadata**: Preserves EXIF data with `exiftool`.
- **Backup**: Back up files and Photos library before running.