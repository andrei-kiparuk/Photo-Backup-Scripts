# Sort Files by Date Script

## Description
This Python script sorts media files into `YYYY/MM/DD` folders based on EXIF metadata or file dates. It uses `exiftool` for accurate date extraction and supports a wide range of extensions.

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
python3 sort_files_by_date.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 sort_files_by_date.py /Volumes/T7/to import
```
Moves `video.mp4` to `/Volumes/T7/to import/2023/05/27/video.mp4` based on EXIF date.

## Notes
- **Date Priority**: Uses EXIF `DateTimeOriginal`; falls back to file date.
- **Backup**: Back up files before running.
- **Error Handling**: Logs invalid dates to console.