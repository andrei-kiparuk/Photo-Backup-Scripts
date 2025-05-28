# Sort File Script

## Description
This Bash script sorts media files into `YYYY/MM/DD` folders based on file creation or modification dates. It’s a lightweight alternative to Python scripts, using `exiftool` for metadata when available.

## Prerequisites
- **Operating System**: macOS or Linux
- **Dependencies**:
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
./sortfile.sh /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
./sortfile.sh /Volumes/T7/to import
```
Moves `photo.jpg` to `/Volumes/T7/to import/2023/05/27/photo.jpg` based on creation date.

## Notes
- **Date Priority**: Uses EXIF if available; falls back to file date.
- **Backup**: Back up files before running.
- **Error Handling**: Logs issues to console.