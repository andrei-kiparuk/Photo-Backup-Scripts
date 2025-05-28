# Export iCloud Photos Delete Script

## Description
This Python script exports iCloud photos and videos from the macOS Photos app using `osxphotos`, then deletes them from the Photos library. It organizes files into `YYYY/MM/DD` folders and preserves metadata with `exiftool`.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - Python 3.6+
  - `osxphotos`: Install via `pip install osxphotos`
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folders**:
  - Export: `/Volumes/G-DRIVE/iCloudExport` (write access)
- **Permissions**: Read/write access to Photos library; write access to export folder

## Usage
Run the script to export and delete photos.

### Command
```bash
python3 export_icloud_photos_delete.py
```

### Parameters
- None (hardcoded export path)

### Example
```bash
python3 export_icloud_photos_delete.py
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27` and deletes them from Photos library.

## Notes
- **Deletion**: Permanently removes exported photos from Photos library.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export.