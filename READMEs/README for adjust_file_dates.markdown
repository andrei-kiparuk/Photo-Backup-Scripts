# Adjust File Dates Script

## Description
This Python script adjusts the creation and modification dates of photos and videos in `/Volumes/T7/to import` and its subfolders to match the `YYYY/MM/DD` structure of their containing folders. It targets specific file extensions and preserves the original time of day.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**: Python 3.6+ (no external libraries required)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Folder Structure**: Files must be in subfolders named `YYYY/MM/DD` (e.g., `2023/05/27`)

## Usage
Run the script to update file dates based on folder structure.

### Command
```bash
python3 adjust_file_dates.py
```

### Parameters
- None (hardcoded base path)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.cr2`, `.dng`, `.heic`, `.tif`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`, `.3gp`

### Example
```bash
python3 adjust_file_dates.py
```
Updates the creation/modification date of `/Volumes/T7/to import/2023/05/27/photo.jpg` to `2023-05-27`, retaining the original time (e.g., `14:30:00`).

## Notes
- **Folder Format**: Folders must follow `YYYY/MM/DD`; invalid formats are skipped with a warning.
- **Time Preservation**: Only the date is updated; the original time is retained.
- **Permissions**: Ensure write access to files in `/Volumes/T7/to import`.
- **Error Handling**: Invalid dates or inaccessible files are logged to the console.