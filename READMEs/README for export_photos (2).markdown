# Export Photos Script

## Description
This Python script exports photos and videos from the macOS Photos app using `osxphotos`, organizing them into `YYYY/MM/DD` folders. It preserves metadata with `exiftool` and supports iCloud downloads.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `osxphotos`: Install via `pip install osxphotos`
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folders**:
  - Export: `/Volumes/G-DRIVE/iCloudExport` (write access)
- **Permissions**: Read access to Photos library; write access to export folder

## Usage
Run the script to export photos.

### Command
```bash
python3 export_photos.py
```

### Parameters
- None (hardcoded export path)

### Example
```bash
python3 export_photos.py
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27`, preserving metadata.

## Notes
- **iCloud**: Downloads missing files if `--download-missing` is enabled.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export.