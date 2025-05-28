# Sort Photos by Content Date Slow Script

## Description
A slower but more thorough version of `sort_photos_by_content_date.py`, this Python script sorts photos into `YYYY/MM/DD` folders using EXIF content dates. It checks multiple EXIF fields for accuracy.

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
python3 sort_photos_by_content_date_slow.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with photos (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`, `.webp`

### Example
```bash
python3 sort_photos_by_content_date_slow.py /Volumes/T7/to import
```
Moves `photo.jpg` to `/Volumes/T7/to import/2023/05/27/photo.jpg` based on EXIF date.

## Notes
- **Thoroughness**: Checks multiple EXIF fields (e.g., `DateTimeOriginal`, `CreateDate`).
- **Performance**: Slower due to extensive metadata checks.
- **Backup**: Back up files before running.