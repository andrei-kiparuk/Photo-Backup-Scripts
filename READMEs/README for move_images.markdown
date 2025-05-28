# Move Images Script

## Description
This PowerShell script moves image files to a destination folder, organizing them into `YYYY/MM/DD` folders based on file creation or modification dates. It’s designed for Windows-based photo organization.

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
.\move_images.ps1 -SourcePath D:\Icloud -DestPath D:\Processed
```

### Parameters
- `-SourcePath`: Path to the folder containing images (default: `D:\Icloud`)
- `-DestPath`: Path to the destination folder (default: `D:\Processed`)

### Supported File Extensions
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.tiff`

### Example
```powershell
.\move_images.ps1 -SourcePath D:\Icloud -DestPath D:\Processed
```
Moves `photo.jpg` to `D:\Processed\2023\05\27\photo.jpg` based on creation date.

## Notes
- **Date Source**: Uses creation date; falls back to modification date.
- **Backup**: Back up files before running.
- **Error Handling**: Logs inaccessible files to console.