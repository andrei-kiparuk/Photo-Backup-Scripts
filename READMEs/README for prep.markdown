# Prep Script

## Description
This Bash script prepares a folder for media processing by creating necessary subfolders (e.g., `Converted`, `Processed`) and verifying dependencies like `ffmpeg` and `exiftool`. It’s a setup step for other scripts.

## Prerequisites
- **Operating System**: macOS or Linux
- **Dependencies**:
  - `ffmpeg`: Install via Homebrew (`brew install ffmpeg`)
  - `exiftool`: Install via Homebrew (`brew install exiftool`)
- **Folder**: `/Volumes/T7` (write access)
- **Permissions**: Write access to base folder

## Usage
Run the script to set up folders and check dependencies.

### Command
```bash
./prep.sh /Volumes/T7
```

### Parameters
- `/path/to/base`: Path to the base folder (default: `/Volumes/T7`)

### Example
```bash
./prep.sh /Volumes/T7
```
Creates `/Volumes/T7/Converted`, `/Volumes/T7/Processed`, and verifies `ffmpeg` and `exiftool`.

## Notes
- **Setup**: Run before other processing scripts.
- **Error Handling**: Exits with error if dependencies are missing.
- **Backup**: Ensure disk has sufficient space.