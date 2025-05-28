# Uninstall Google Drive Script

## Description
This Bash script uninstalls Google Drive from a macOS system, removing its application and configuration files. It’s useful for cleaning up before reprocessing Google Takeout data.

## Prerequisites
- **Operating System**: macOS
- **Dependencies**: None (uses built-in `rm` and `killall`)
- **Permissions**: Admin access to remove Google Drive files

## Usage
Run the script with sudo to uninstall Google Drive.

### Command
```bash
sudo ./uninstall_google_drive.sh
```

### Parameters
- None

### Example
```bash
sudo ./uninstall_google_drive.sh
```
Removes Google Drive app and configs from `/Applications` and `~/Library`.

## Notes
- **Admin Access**: Requires sudo to delete system files.
- **Backup**: Back up Google Drive data before running.
- **Error Handling**: Logs removal failures to console.