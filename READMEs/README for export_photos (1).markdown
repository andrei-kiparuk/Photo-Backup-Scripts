# Export Photos Script

## Description
This Bash script exports photos and videos from the macOS Photos app to an external drive, organizing them into a `YYYY/MM/DD-location` folder structure. It uses `osxphotos` to preserve metadata, download files from iCloud, and optionally delete exported files from the Photos library. The script logs progress and errors for tracking.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**:
  - `osxphotos`: Install via `pip install osxphotos`
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **External Drive**: Mounted at `/Volumes/G-DRIVE/iCloudExport`
- **Permissions**: Write access to the export path and read access to the Photos library

## Usage
Run the script from the command line to export photos and videos.

### Command
```bash
./export_photos.sh
```

### Parameters
- None (hardcoded paths and options)

### Environment Variables
- None required, but ensure the Photos app is not running during export to avoid conflicts.

### Configuration
Edit the script to modify:
- **Export Path**: Default is `/Volumes/G-DRIVE/iCloudExport`
- **Log File**: Default is `/Volumes/G-DRIVE/iCloudExport/export.log`
- **Folder Template**: Default is `{created.year}/{created.mm}/{created.dd}-{place.name|unknown}`

### Options Used
- `--download-missing`: Downloads original files from iCloud
- `--exiftool`: Updates file metadata using `exiftool`
- `--exiftool-option "-m"`: Ignores minor `exiftool` errors
- `--live`: Exports both HEIC and HEVC components of live photos
- `--post-function delete_photo.py`: Deletes exported photos from the Photos library
- `--verbose`: Logs detailed progress to console and file
- `--report`: Generates a report for diagnostic purposes

### Example
```bash
./export_photos.sh
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023/05/27-London`, logs to `export.log`, and deletes exported files from the Photos library.

## Notes
- **Backup**: Always back up your Photos library before running (use Time Machine or similar).
- **Version**: Ensure `osxphotos` is updated (`pip install --upgrade osxphotos`) for compatibility with `--post-function`.
- **Errors**: Check `export.log` for issues like missing iCloud files or `exiftool` warnings.
- **File Formats**: Supports HEIC, JPEG, and HEVC (live photos) natively; other formats may require additional handling.
- **Post-Function**: Requires `delete_photo.py` in the same directory for library deletion (not included in this repo).