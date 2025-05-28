# Import Single File Script

## Description
This AppleScript imports a single media file into the macOS Photos app, preserving metadata. It prompts the user to select a file and imports it without moving the original.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**: None (uses built-in Photos app)
- **Permissions**: Read access to source file; Photos app access

## Usage
Run the script using the Script Editor or command line.

### Command
```bash
osascript import_single_file.applescript
```

### Parameters
- None (prompts for file selection)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.m4v`

### Example
```bash
osascript import_single_file.applescript
```
Prompts user to select `photo.jpg`, then imports it to Photos app.

## Notes
- **Photos App**: Must be running during execution.
- **Backup**: Back up Photos library before running.
- **Manual**: Best for one-off imports.