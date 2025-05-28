# Sort Videos by Content Date Script

## Description
This Python script sorts videos into `YYYY/MM/DD` folders based on EXIF or embedded metadata content dates. It uses `exiftool` for metadata extraction and targets video extensions.

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
python3 sort_videos_by_content_date.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with videos (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 sort_videos_by_content_date.py /Volumes/T7/to import
```
Moves `video.mp4` to `/Volumes/T7/to import/2023/05/27/video.mp4` based on metadata date.

## Notes
- **Date Priority**: Uses embedded metadata (e.g., `CreationDate`).
- **Backup**: Back up files before running.
- **Error Handling**: Skips files without metadata; logs to console.