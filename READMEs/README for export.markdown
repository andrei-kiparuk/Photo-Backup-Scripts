# Export Script

## Description
This AppleScript exports photos and videos from the macOS Photos app to a specified folder, using the Photos app’s native export functionality. It organizes files by date and preserves metadata.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**: None (uses built-in Photos app)
- **Folders**:
  - Export: `/Volumes/G-DRIVE/iCloudExport` (write access)
- **Permissions**: Read access to Photos library; write access to export folder

## Usage
Run the script using the Script Editor or command line.

### Command
```bash
osascript export.scpt
```

### Parameters
- None (hardcoded export path)

### Example
```bash
osascript export.scpt
```
Exports photos to `/Volumes/G-DRIVE/iCloudExport/2023-05-27`, preserving metadata.

## Notes
- **Photos App**: Must be running during execution.
- **Backup**: Back up Photos library before running.
- **Customization**: Edit script to change export path or options.