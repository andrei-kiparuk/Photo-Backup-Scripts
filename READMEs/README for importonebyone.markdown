# Import One by One Script

## Description
This AppleScript imports media files one by one into the macOS Photos app, prompting the user to select each file. It preserves metadata and is useful for manual, selective imports.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**: None (uses built-in Photos app)
- **Permissions**: Read access to source files; Photos app access

## Usage
Run the script using the Script Editor or command line.

### Command
```bash
osascript importonebyone.scpt
```

### Parameters
- None (prompts for file selection)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.tiff`
- **Videos**: `.mp4`, `.mov`, `.m4v`

### Example
```bash
osascript importonebyone.scpt
```
Prompts user to select `video.mp4`, then imports it to Photos app.

## Notes
- **Photos App**: Must be running during execution.
- **Backup**: Back up Photos library before running.
- **Manual**: Best for small, selective imports.