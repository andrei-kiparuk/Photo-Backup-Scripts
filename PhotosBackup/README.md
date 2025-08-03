# Large Archive Photo Import System

A comprehensive solution for importing large photo archives (8TB+) into macOS Photos with intelligent date handling, duplicate detection, and resumable processing.

## Features

- **Batch Processing**: Processes photos in 50GB batches to manage disk space
- **Intelligent Date Handling**: Extracts dates from folder structure, EXIF data, and metadata files
- **Duplicate Detection**: Prevents importing duplicate files based on content hash
- **Resumable**: Can be stopped and resumed from where it left off
- **Multi-PC Support**: Progress tracking works across multiple computers
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Album Organization**: Imports all photos to "import2025" album for easy management

## Requirements

- macOS 10.15 or later
- Homebrew (for dependency installation)
- At least 10GB free disk space for processing
- SlowDisk mounted at `/Volumes/SlowDisk`

## Quick Start

1. **Setup Environment**:
   ```bash
   ./setup_import.sh
   ```

2. **Start Import**:
   ```bash
   ./import_large_archive.sh
   ```

3. **Monitor Progress**:
   ```bash
   python3 import_status.py status
   ```

4. **View Logs**:
   ```bash
   python3 import_status.py logs
   ```

## File Structure

```
PhotosBackup/
├── import_large_archive.sh    # Main import script
├── date_fixer.py              # Date extraction and duplicate detection
├── import_status.py           # Progress monitoring and management
├── setup_import.sh            # Environment setup
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Configuration

### Source Directory
The script expects photos to be organized in the following structure:
```
/Volumes/SlowDisk/iCloud/
├── 2020/
│   ├── 01/
│   │   ├── 01/
│   │   │   ├── photo1.jpg
│   │   │   └── photo2.jpg
│   │   └── 02/
│   └── 02/
└── 2021/
    └── ...
```

### Batch Size
Default batch size is 50GB. You can modify this in `import_large_archive.sh`:
```bash
BATCH_SIZE_GB=50
```

### Album Name
Photos are imported to the "import2025" album. Change this in `import_large_archive.sh`:
```bash
ALBUM_NAME="import2025"
```

## Usage

### Starting the Import

```bash
./import_large_archive.sh
```

The script will:
1. Check dependencies and disk space
2. Load or create progress tracking
3. Process folders in chronological order
4. Import photos in batches
5. Handle duplicates and date correction
6. Restart Photos app periodically

### Monitoring Progress

```bash
# Check current status
python3 import_status.py status

# View recent logs
python3 import_status.py logs

# View more log lines
python3 import_status.py logs --lines 100
```

### Managing the Import

```bash
# Pause the import
python3 import_status.py pause

# Resume the import
python3 import_status.py resume

# Reset progress (start from beginning)
python3 import_status.py reset
```

## How It Works

### Date Extraction Priority
1. **Folder Structure**: YYYY/MM/DD from path
2. **Filename Patterns**: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, WP_YYYYMMDD
3. **EXIF Data**: DateTimeOriginal, CreateDate, ModifyDate
4. **Metadata Files**: Associated .json, .xml, .txt files
5. **Oldest Date**: Uses the earliest date found

### Duplicate Detection
- Computes SHA-256 hash of file content
- Skips files with identical hashes
- Keeps the first occurrence of each unique file

### Batch Processing
- Processes folders in chronological order
- Groups folders until batch size (50GB) is reached
- Imports batch to Photos app
- Cleans up temporary files
- Continues with next batch

### Resumability
- Progress tracked in JSON file
- Can be stopped and resumed
- Works across multiple computers
- Atomic updates prevent corruption

## Troubleshooting

### Common Issues

**"Missing dependencies"**
```bash
./setup_import.sh
```

**"Low disk space"**
- Free up space on your system drive
- The script needs at least 10GB for processing

**"Photos app not responding"**
- The script automatically restarts Photos every 5 batches
- You can manually restart Photos if needed

**"Import failed"**
- Check logs: `python3 import_status.py logs`
- The script will retry failed imports
- Check disk space and Photos app status

### Log Files

- **Progress**: `/Volumes/SlowDisk/iCloud/import_progress.json`
- **Logs**: `/Volumes/SlowDisk/iCloud/import_log.txt`

### Performance Tips

1. **Close other applications** to free up system resources
2. **Ensure stable internet connection** for iCloud sync
3. **Monitor disk space** regularly
4. **Use SSD storage** for better performance

## Advanced Configuration

### Custom Source Directory
Edit `import_large_archive.sh`:
```bash
SOURCE_DIR="/path/to/your/photos"
```

### Custom Batch Size
Edit `import_large_archive.sh`:
```bash
BATCH_SIZE_GB=25  # Smaller batches for less disk space
```

### Custom Album Name
Edit `import_large_archive.sh`:
```bash
ALBUM_NAME="My Photo Import"
```

## Safety Features

- **Atomic Updates**: Progress file updates are atomic
- **Signal Handling**: Graceful shutdown on interruption
- **Error Recovery**: Automatic retries for failed operations
- **Backup Creation**: Progress files are backed up before reset
- **Disk Space Monitoring**: Stops when disk space is low

## Support

If you encounter issues:

1. Check the logs: `python3 import_status.py logs`
2. Verify dependencies: `./setup_import.sh`
3. Check disk space: `df -h`
4. Restart Photos app manually if needed

## License

This project is provided as-is for personal use. Please ensure you have proper backups before running large import operations. 