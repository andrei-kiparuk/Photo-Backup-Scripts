# Next Step Script

## Description
This Python script processes media files as part of a multi-step workflow, adjusting dates or metadata and moving files to a designated folder. Its exact purpose is unclear but likely prepares files for import or conversion.

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
python3 nextstep.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 nextstep.py /Volumes/T7/to import
```
Processes `photo.jpg` and moves it to `/Volumes/T7/processed/2023/05/27/photo.jpg`.

## Notes
- **Ambiguity**: Clarify script’s role in your workflow for precise documentation.
- **Backup**: Back up files before running.
- **Error Handling**: Logs issues to console.