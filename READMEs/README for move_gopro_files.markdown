# Move GoPro Files Script

## Description
This PowerShell script moves GoPro video files (e.g., `.mp4` from GoPro cameras) to a destination folder, organizing them into `YYYY/MM/DD` folders based on file dates. It’s designed for Windows-based GoPro media management.

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
.\move_gopro_files.ps1 -SourcePath D:\Icloud -DestPath D:\Processed
```

### Parameters
- `-SourcePath`: Path to the folder containing GoPro files (default: `D:\Icloud`)
- `-DestPath`: Path to the destination folder (default: `D:\Processed`)

### Supported File Extensions
- **Videos**: `.mp4`, `.mov`

### Example
```powershell
.\move_gopro_files.ps1 -SourcePath D:\Icloud -DestPath D:\Processed
```
Moves `GOPR1234.mp4` to `D:\Processed\2023\05\27\GOPR1234.mp4` based on creation date.

## Notes
- **GoPro Specific**: Filters files with GoPro naming conventions (e.g., `GOPR*`).
- **Backup**: Back up files before running.
- **Error Handling**: Logs inaccessible files to console.