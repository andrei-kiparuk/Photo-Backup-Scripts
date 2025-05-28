# Move AVI Script

## Description
This PowerShell script moves `.avi` video files from a source folder to a destination folder, organizing them into `YYYY/MM/DD` folders based on file creation or modification dates. It’s designed for Windows-based media organization.

## Prerequisites
- **Operating System**: Windows
- **Dependencies**: None (uses built-in PowerShell)
- **Folders**:
  - Source: `D:\Icloud` (read access)
  - Destination: `D:\Processed` (write access)
- **Permissions**: Read/write access to both folders

## Usage
Run the script in PowerShell, specifying the source and destination folders.

### Command
```powershell
.\move_avi.ps1 -SourcePath D:\Icloud -DestPath D:\Processed
```

### Parameters
- `-SourcePath`: Path to the folder containing `.avi` files (default: `D:\Icloud`)
- `-DestPath`: Path to the destination folder (default: `D:\Processed`)

### Supported File Extensions
- **Videos**: `.avi`

### Example
```powershell
.\move_avi.ps1 -SourcePath D:\Icloud -DestPath D:\Processed
```
Moves `video.avi` from `D:\Icloud` to `D:\Processed\2023\05\27\video.avi` based on its creation date.

## Notes
- **Date Source**: Uses file creation date; falls back to modification date if needed.
- **Backup**: Back up files before running to prevent data loss.
- **Error Handling**: Logs inaccessible files to console.