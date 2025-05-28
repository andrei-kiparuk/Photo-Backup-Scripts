# Export iCloud Photos Script

## Description
This Python script exports photos and videos from the macOS Photos app, including iCloud content, using `osxphotos`. It organizes files into `YYYY/MM/DD` folders, downloads missing iCloud files, and preserves metadata with `exiftool`.

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
Run the script to export iCloud photos.

### Command
```bash
python3 export_icloud_photos.py
```

### Parameters
- None (hardcoded export path)

### Example
```bash
python3 export_icloud_photos.py
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27`, downloading iCloud files.

## Notes
- **iCloud**: Requires internet connection for downloading missing files.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export.