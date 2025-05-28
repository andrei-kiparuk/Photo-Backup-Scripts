# Unprocessed Script

## Description
This Python script identifies unprocessed media files (e.g., those not yet converted or imported) and moves them to a designated folder for further processing. Its exact purpose is unclear but likely part of a workflow.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**: Python 3.6+ (no external libraries required)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 uprocessed.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 uprocessed.py /Volumes/T7/to import
```
Moves unprocessed `photo.jpg` to `/Volumes/T7/unprocessed/2023/05/27/photo.jpg`.

## Notes
- **Ambiguity**: Clarify script’s role in your workflow for precise documentation.
- **Backup**: Back up files before running.
- **Error Handling**: Logs issues to console.