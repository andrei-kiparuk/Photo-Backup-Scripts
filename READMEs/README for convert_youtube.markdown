# Convert YouTube Script

## Description
This Python script converts downloaded YouTube videos to HEVC format, organizing them into `YYYY/MM/DD` folders based on metadata or file dates. It uses `ffmpeg` for conversion and `exiftool` for metadata preservation.

## Prerequisites
- **Operating System**: macOS or Windows
- **Dependencies**:
  - Python 3.6+
  - `ffmpeg`: Install via Homebrew (`brew install ffmpeg`) on macOS or download for Windows
  - `exiftool`: Install via Homebrew (`brew install exiftool`) or download for Windows
- **Folders**:
  - Source: `/Volumes/WDsmall/Icloud` (read access)
  - Converted: `/Volumes/JBOD/Converted` (write access)
  - Processed: `/Volumes/WDsmall/Processed` (write access)
- **Permissions**: Read/write access to all folders

## Usage
Run the script, specifying the source folder with YouTube videos.

### Command
```bash
python3 convert_youtube.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with video files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Videos**: `.mp4`, `.webm`, `.mkv`, `.flv`, `.avi`

### Example
```bash
python3 convert_youtube.py /Volumes/WDsmall/Icloud
```
Converts `video.webm` to HEVC, saves to `/Volumes/JBOD/Converted/2023/05/27/video.mp4`, and moves original to `/Volumes/WDsmall/Processed/2023/05/27/video.webm`.

## Notes
- **Metadata**: Limited metadata extraction for YouTube videos; uses file dates as fallback.
- **Backup**: Back up files before running.