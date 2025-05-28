# Convert All 2 Script

## Description
A variant of `convert_all.py`, this Python script converts photos and videos to HEIC (photos) and HEVC (videos), organizing them into `YYYY/MM/DD` folders based on metadata or file dates. It uses `ffmpeg` for video conversion and `pillow_heif` for photos, with enhanced error handling for corrupted files.

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
python3 convert_all_2.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`, `.gif`, `.cr2`, `.dng`, `.heic`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.flv`, `.wmv`, `.mpeg`, `.3gp`, `.m4v`, `.vob`

### Example
```bash
python3 convert_all_2.py /Volumes/WDsmall/Icloud
```
Converts `video.mov` to HEVC, saves it to `/Volumes/JBOD/Converted/2023/05/27/video.mp4`, and moves the original to `/Volumes/WDsmall/Processed/2023/05/27/video.mov`.

## Notes
- **Error Handling**: Skips corrupted files and logs details to console.
- **Metadata**: Preserves EXIF data using `exiftool`.
- **GPU Acceleration**: Uses `hevc_videotoolbox` on macOS if available.
- **Backup**: Back up files before running to prevent data loss.