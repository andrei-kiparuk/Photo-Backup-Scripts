# Convert All A Script

## Description
This Python script converts media files to HEIC (photos) and HEVC (videos), focusing on Apple-specific optimizations (e.g., live photos). It organizes converted files into `YYYY/MM/DD` folders and uses `exiftool` to preserve metadata, with logging for failed conversions.

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
python3 convert_all_a.py /Volumes/WDsmall/Icloud
```

### Parameters
- `/path/to/source`: Path to the folder with media files (defaults to `/Volumes/WDsmall/Icloud`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.heif`, `.cr2`, `.dng`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.m4v`, `.avi`, `.mkv`, `.wmv`

### Example
```bash
python3 convert_all_a.py /Volumes/WDsmall/Icloud
```
Converts `livephoto.heic` to HEIC, saves to `/Volumes/JBOD/Converted/2023/05/27/livephoto.heic`, and moves the original to `/Volumes/WDsmall/Processed/2023/05/27/livephoto.heic`.

## Notes
- **Live Photos**: Optimized for Apple’s live photo formats.
- **Logging**: Failed conversions are logged to `/Volumes/JBOD/Converted/convert.log`.
- **Metadata**: Preserves EXIF and creation dates.
- **Backup**: Back up files before running.