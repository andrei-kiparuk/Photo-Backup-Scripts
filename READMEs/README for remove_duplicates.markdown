# Remove Duplicates Script

## Description
This Python script identifies and removes duplicate media files based on SHA-256 hashes, keeping the file with the earliest date or highest quality. It organizes remaining files into `YYYY/MM/DD` folders.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**: Python 3.6+ (no external libraries required)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 remove_duplicates.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 remove_duplicates.py /Volumes/T7/to import
```
Removes duplicate `photo.jpg`, keeping the earliest version in `/Volumes/T7/to import/2023/05/27`.

## Notes
- **Duplicate Check**: Uses SHA-256 for exact matches.
- **Backup**: Back up files before running to prevent data loss.
- **Error Handling**: Logs deleted files to console.