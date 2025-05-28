# Export Photos Sorted Script

## Description
This Python script exports photos and videos from the macOS Photos app using `osxphotos`, sorting them into `YYYY/MM/DD` folders based on metadata or content dates. It preserves metadata with `exiftool` and supports iCloud downloads.

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
Run the script to export and sort photos.

### Command
```bash
python3 export_photos_sorted.py
```

### Parameters
- None (hardcoded export path)

### Example
```bash
python3 export_photos_sorted.py
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27`, sorted by content date.

## Notes
- **Sorting**: Prioritizes EXIF content dates for folder organization.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export.