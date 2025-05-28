# Remove Similar Script

## Description
This Python script identifies and removes visually similar media files using perceptual hashing (e.g., pHash). It keeps the highest-quality version and organizes files into `YYYY/MM/DD` folders.

## Prerequisites
- **Operating System**: Any (tested on macOS)
- **Dependencies**:
  - Python 3.6+
  - `imagehash`, `pillow`: Install via `pip install imagehash pillow`
- **Folder**: `/Volumes/T7/to import` (read/write access)
- **Permissions**: Read/write access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 remove_similar.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder with media files (default: `/Volumes/T7/to import`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.tiff`

### Example
```bash
python3 remove_similar.py /Volumes/T7/to import
```
Removes similar `photo2.jpg`, keeping `photo1.jpg` in `/Volumes/T7/to import/2023/05/27`.

## Notes
- **Similarity Check**: Uses perceptual hashing for near-duplicate detection.
- **Backup**: Back up files before running to prevent data loss.
- **Error Handling**: Logs deleted files to console.