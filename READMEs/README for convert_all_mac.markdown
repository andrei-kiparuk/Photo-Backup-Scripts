# Convert All Mac Script

## Description
This Python script converts media files to HEIC and HEVC, optimized for macOS Photos app compatibility. It organizes files into `YYYY/MM/DD` folders, preserves metadata with `exiftool`, and uses macOS-native GPU acceleration for conversions.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `pillow`, `pillow_heif`: Install via `pip install pillow pillow_heif`
  - `ffmpeg`: Install via Homebrew (`brew install ffmpeg`)
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folders**:
  - Source: `/Volumes/WDsmall/Icloud` (read access)
  - Converted: `/Volumes/JBOD/Converted` (write access)
  - Processed: `/Volumes/WDsmall/Processed` (write access)
- **Permissions**: Read/write access to all folders

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 convert_all_mac.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.m4v`, `.avi`, `.mkv`, `.wmv`

### Example
```bash
python3 convert_all_mac.py /Volumes/WDsmall/Icloud
```
Converts `video.mov` to HEVC, saves to `/Volumes/JBOD/Converted/2023/05/27/video.mp4`, and moves original to `/Volumes/WDsmall/Processed/2023/05/27/video.mov`.

## Notes
- **GPU Acceleration**: Uses `hevc_videotoolbox` for faster conversions.
- **Metadata**: Preserves EXIF data with `exiftool`.
- **Backup**: Back up files before running.