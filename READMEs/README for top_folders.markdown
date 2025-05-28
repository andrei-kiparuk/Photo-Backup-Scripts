# Top Folders Script

## Description
This Bash script lists the top-level folders in a specified directory, useful for auditing folder structures before processing media files. It outputs folder names and their creation dates.

## Prerequisites
- **Operating System**: macOS or Linux
- **Dependencies**: None (uses built-in `ls` and `stat`)
- **Folder**: `/Volumes/T7/to import` (read access)
- **Permissions**: Read access to source folder

## Usage
Run the script, specifying the source folder.

### Command
```bash
./top_folders.sh /Volumes/T7/to import
```

### Parameters
- `/path/to/source`: Path to the folder to scan (default: `/Volumes/T7/to import`)

### Example
```bash
./top_folders.sh /Volumes/T7/to import
```
Outputs: `2023 2023-05-27T12:00:00`

## Notes
- **Use Case**: Run to verify folder structure before other scripts.
- **Output**: Lists folders in chronological order.
- **Error Handling**: Skips inaccessible folders.