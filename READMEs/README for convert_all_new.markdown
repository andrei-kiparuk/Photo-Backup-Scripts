# Convert All New Script

## Description
This Python script converts media files to HEIC and HEVC, with updated logic for handling new file formats (e.g., WebP) and improved metadata extraction. It organizes files into `YYYY/MM/DD` folders and uses `exiftool` for metadata preservation.

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
python3 convert_all_new.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 convert_all_new.py /Volumes/WDsmall/Icloud
```
Converts `photo.webp` to HEIC, saves to `/Volumes/JBOD/Converted/2023/05/27/photo.heic`, and moves original to `/Volumes/WDsmall/Processed/2023/05/27/photo.webp`.

## Notes
- **New Formats**: Adds support for `.webp` images.
- **Metadata**: Improved EXIF extraction with `exiftool`.
- **Backup**: Back up files before running.