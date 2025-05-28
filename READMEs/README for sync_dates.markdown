# Sync Dates Script

## Description
This Python script adjusts the creation and modification dates of photos and videos in `/Volumes/T7/to import` and its subfolders to match the `YYYY/MM/DD` structure of their containing folders. It processes files with specific extensions, preserving the original time of day.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**:
  - Python 3.6+
  - No external libraries required
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Folder Structure**: Files must be in subfolders named `YYYY/MM/DD` (e.g., `2023/05/27`)

## Usage
Run the script to update file dates based on folder structure.

### Command
```bash
python3 sync_dates.py
```

### Parameters
- None (hardcoded base path)

### Environment Variables
- None required

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.cr2`, `.dng`, `.heic`, `.tif`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`, `.3gp`

### Example
```bash
python3 sync_dates.py
```
Updates the creation/modification date of `/Volumes/T7/to import/2023/05/27/photo.jpg` to `2023-05-27`, keeping the original time (e.g., `14:30:00`).

## Notes
- **Folder Format**: Folders must strictly follow `YYYY/MM/DD`; invalid formats are skipped with a warning.
- **Time Preservation**: The script retains the original time of day, only updating the date.
- **Permissions**: Ensure write access to files in `/Volumes/T7/to import`.
- **Dry Run**: Test with a small folder to verify behavior before processing large datasets.
- **Error Handling**: Invalid dates or inaccessible files are logged to the console.