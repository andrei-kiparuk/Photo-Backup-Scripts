# Export Photos Old Script

## Description
This Bash script exports photos and videos from the macOS Photos app using `osxphotos`, organizing them into `YYYY/MM/DD` folders. It’s an older version of `export_photos.sh` with simpler options and no deletion functionality.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - `osxphotos`: Install via `pip install osxphotos`
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folders**:
  - Export: `/Volumes/G-DRIVE/iCloudExport` (write access)
- **Permissions**: Read access to Photos library; write access to export folder

## Usage
Run the script to export photos.

### Command
```bash
./export_photos_old.sh
```

### Parameters
- None (hardcoded export path)

### Example
```bash
./export_photos_old.sh
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27`, preserving metadata.

## Notes
- **Legacy**: Use `export_photos.sh` for newer features like deletion.
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export.