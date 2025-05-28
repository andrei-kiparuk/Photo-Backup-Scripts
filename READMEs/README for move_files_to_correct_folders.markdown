# Move Files to Correct Folders Script

## Description
This Python script moves media files to `YYYY/MM/DD` folders based on their EXIF metadata or file creation dates. It corrects misorganized files by aligning them with their content dates, targeting specific photo and video extensions.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**:
  - Python 3.6+
  - `exiftool`: Install via Homebrew (`brew install exiftool`) on macOS or download for Windows
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 move_files_to_correct_folders.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python3 move_files_to_correct_folders.py /Volumes/T7/to import
```
Moves `photo.jpg` from `/Volumes/T7/to import/misc` to `/Volumes/T7/to import/2023/05/27/photo.jpg` based on EXIF date.

## Notes
- **Date Priority**: Uses EXIF `DateTimeOriginal`; falls back to file creation date.
- **Backup**: Back up files before running to avoid data loss.
- **Error Handling**: Skips files without valid dates; logs to console.