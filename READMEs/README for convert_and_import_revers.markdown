# Convert and Import Reverse Script

## Description
This Python script imports media files into the macOS Photos app using `osxphotos`, then converts them to HEIC and HEVC, reversing the typical workflow. It organizes files into `YYYY/MM/DD` folders and preserves metadata with `exiftool`.

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
python3 convert_and_import_revers.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_and_import_revers.py /Volumes/WDsmall/Icloud
```
Imports `photo.jpg` to Photos app, converts to HEIC, and saves to `/Volumes/JBOD/Converted/2023/05/27/photo.heic`.

## Notes
- **Workflow**: Imports first, then converts, useful for Photos app metadata syncing.
- **Metadata**: Preserves EXIF data with `exiftool`.
- **Backup**: Back up files and Photos library before running.