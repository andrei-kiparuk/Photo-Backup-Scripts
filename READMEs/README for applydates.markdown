# Apply Dates Script

## Description
This Bash script updates the creation and modification dates of media files based on their EXIF metadata or folder structure (`YYYY/MM/DD`). It uses `exiftool` to extract dates and `touch` to set file system dates, targeting specific photo and video extensions.

## Prerequisites
- **Operating System**: macOS or Linux
- **Dependencies**:
  - `exiftool`: Install via Homebrew (`brew install exiftool`) on macOS
  - `touch`: Available by default on macOS/Linux
- **Folder**: Source folder with media files in `YYYY/MM/DD` structure
- **Permissions**: Read/write access to the source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
./applydates.sh /path/to/source
```

### Parameters
- `/path/to/source`: Path to the folder with media files

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tif`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`, `.3gp`

### Example
```bash
./applydates.sh /Volumes/T7/source
```
Sets the creation date of `photo.jpg` to its EXIF `DateTimeOriginal` or folder date `2023/05/27`.

## Notes
- **Priority**: Uses EXIF `DateTimeOriginal` first, then folder date as fallback.
- **Permissions**: Ensure `exiftool` and `touch` have access to modify files.
- **Error Handling**: Skips files without valid dates; logs errors to console.
- **Backup**: Back up files before running to avoid unintended changes.