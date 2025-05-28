# Custom Export Script

## Description
This Python script exports photos and videos from the macOS Photos app using `osxphotos`, with customizable export options (e.g., folder structure, metadata). It organizes files into user-defined folders and preserves metadata with `exiftool`.

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
Run the script to export media files.

### Command
```bash
python3 custom_export.py
```

### Parameters
- None (hardcoded export path and options)

### Configuration
Edit the script to modify:
- **Export Path**: Default is `/Volumes/G-DRIVE/iCloudExport`
- **Folder Template**: Default is `{created.year}/{created.mm}/{created.dd}-{place.name|unknown}`

### Example
```bash
python3 custom_export.py
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27-London`, preserving metadata.

## Notes
- **Customization**: Modify script for specific `osxphotos` options (e.g., `--download-missing`).
- **Backup**: Back up Photos library before running.
- **Photos App**: Close Photos app during export to avoid conflicts.