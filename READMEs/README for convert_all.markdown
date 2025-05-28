# Convert All Script

## Description
This Python script converts photos and videos in a source folder to HEIC (photos) and HEVC (videos) formats, preserving metadata using `exiftool`. It organizes converted files into a `YYYY/MM/DD` folder structure based on metadata or original dates and moves original files to a processed folder.

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
- **Permissions**: Read/write access to all specified folders

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 convert_all.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`, `.gif`, `.cr2`, `.dng`, `.heic`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.flv`, `.wmv`, `.mpeg`, `.3gp`, `.m4v`, `.vob`

### Example
```bash
python3 convert_all.py /Volumes/WDsmall/Icloud
```
Converts `photo.jpg` to HEIC, organizes it in `/Volumes/JBOD/Converted/2023/05/27/photo.heic`, and moves the original to `/Volumes/WDsmall/Processed/2023/05/27/photo.jpg`.

## Notes
- **GPU Acceleration**: Uses `hevc_videotoolbox` on macOS for video conversion if available, else falls back to `libx265`.
- **Metadata**: Preserves EXIF and creation dates using `exiftool`.
- **Error Handling**: Failed conversions are logged; files remain in source folder.
- **Backup**: Back up files before running to prevent data loss.