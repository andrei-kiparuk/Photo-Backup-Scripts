# Export iCloud Photos Updated Script

## Description
An updated version of `export_icloud_photos.py`, this Python script exports iCloud photos and videos with improved error handling and logging. It organizes files into `YYYY/MM/DD` folders using `osxphotos` and preserves metadata with `exiftool`.

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
python3 export_icloud_photos_updated.py
```

### Parameters
- None (hardcoded export path)

### Example
```bash
python3 export_icloud_photos_updated.py
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27`, logging errors to console.

## Notes
- **Logging**: Detailed error logs for failed exports.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export.