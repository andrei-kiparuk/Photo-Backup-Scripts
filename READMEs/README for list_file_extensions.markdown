# List File Extensions Script

## Description
This Python script scans a folder and its subfolders, listing all unique file extensions found. It outputs the results to the console, useful for auditing media files before processing.

## Prerequisites
- **Operating System**: Any
- **Dependencies**: Python 3.6+ (no external libraries required)
- **Folder**: `/Volumes/T7/to import` (read access)
- **Permissions**: Read access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
python3 list_file_extensions.py /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder to scan (defaults to `/Volumes/T7/to import`)

### Example
```bash
python3 list_file_extensions.py /Volumes/T7/to import
```
Outputs: `.jpg .png .mp4 .mov`

## Notes
- **Output**: Lists unique extensions in alphabetical order.
- **Use Case**: Run before other scripts to verify supported file types.
- **Error Handling**: Skips inaccessible files.