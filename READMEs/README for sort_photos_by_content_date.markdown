# Sort Photos by Content Date Script

## Description
This Python script sorts photos into `YYYY/MM/DD` folders based on EXIF content dates (e.g., `DateTimeOriginal`). It uses `exiftool` for metadata extraction and targets photo extensions.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**:
  - Python 3.6+
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 sort_photos_by_content_date.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with photos (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`, `.webp`

### Example
```bash
python3 sort_photos_by_content_date.py /Volumes/T7/to import
```
Moves `photo.jpg` to `/Volumes/T7/to import/2023/05/27/photo.jpg` based on EXIF date.

## Notes
- **Date Priority**: Uses EXIF `DateTimeOriginal` only.
- **Backup**: Back up files before running.
- **Error Handling**: Skips files without EXIF; logs to console.