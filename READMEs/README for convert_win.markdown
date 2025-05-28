# Convert Win Script

## Description
This Python script converts media files to HEIC and HEVC on Windows, organizing files into `YYYY/MM/DD` folders based on metadata or file dates. It uses `ffmpeg` for video conversion and `exiftool` for metadata preservation.

## Prerequisites
- **Operating System**: Windows
- **Dependencies**:
  - Python 3.6+
  - `pillow`, `pillow_heif`: Install via `pip install pillow pillow_heif`
  - `ffmpeg`: Download and add to PATH
  - `exiftool`: Download and add to PATH
- **Folders**:
  - Source: `D:\Icloud` (read access)
  - Converted: `D:\Converted` (write access)
  - Processed: `D:\Processed` (write access)
- **Permissions**: Read/write access to all folders

## Usage
Run the script, specifying the source folder.

### Command
```bash
python convert_win.py D:\Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `D:\Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`

### Example
```bash
python convert_win.py D:\Icloud
```
Converts `photo.jpg` to HEIC, saves to `D:\Converted\2023\05\27\photo.heic`, and moves original to `D:\Processed\2023\05\27\photo.jpg`.

## Notes
- **Windows Paths**: Uses backslashes (`\`) for paths.
- **Metadata**: Preserves EXIF data with `exiftool`.
- **Backup**: Back up files before running.