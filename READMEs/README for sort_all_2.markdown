# Sort All 2 Script

## Description
A variant of `sort_all.py`, this Python script sorts media files into `YYYY/MM/DD` folders with improved handling of missing metadata. It uses `exiftool` and falls back to folder names or file dates.

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
python3 sort_all_2.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 sort_all_2.py /Volumes/T7/to import
```
Moves `video.mp4` to `/Volumes/T7/to import/2023/05/27/video.mp4` using folder name as fallback.

## Notes
- **Fallback**: Uses folder names (`YYYY/MM/DD`) if metadata is missing.
- **Backup**: Back up files before running.
- **Error Handling**: Logs issues to console.