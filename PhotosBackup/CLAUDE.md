# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the Large Archive Photo Import System for importing large photo/video archives (8TB+) into macOS Photos. The system provides intelligent date handling, duplicate detection, batch processing, and resumable imports with progress tracking across multiple computers.

## Architecture Overview

### Core Components

**Orchestration Layer (Bash)**
- `import_large_archive.sh` - Main entry point that orchestrates the entire import workflow
- Performs pre-flight checks (dependencies, disk space, source directory validity)
- Manages progress tracking and state management
- Handles batch processing coordination and Photos app lifecycle
- Requires virtual environment: `source ./venv/bin/activate`

**Processing Layer (Python)**
- `date_fixer.py` - Core processing engine that handles:
  - Multi-layer date extraction (folder path → filename → EXIF → metadata files)
  - File copying with date fixing
  - Duplicate detection via SHA-256 content hashing
  - Temporary directory management for import batches
- `import_status.py` - Progress monitoring and management tool
  - Reads/writes JSON tracking files
  - Shows real-time status, logs, and time estimates
  - Provides pause/resume/reset functionality

**Tracking System (JSON-based)**
- `import_progress.json` - Tracks processed folders, file counts, sizes, failures
- `folder_index.json` - Pre-computed index of all folders with media, sizes, and file counts
- Files stored on SMB share (`/Volumes/SlowDisk/iCloud/`) to enable cross-PC resumability

### Processing Flow

1. **Index Creation**: Scan source directory → create folder_index.json with stats
2. **Batch Selection**: Read folder_index.json → filter processed folders → select folders up to BATCH_SIZE_GB (50GB)
3. **Date Fixing**: Copy files to temp dir → apply date corrections using date_fixer.py
4. **Photos Import**: Use osxphotos CLI to import temp directory → skip duplicates
5. **Progress Update**: Mark folders as processed → update totals → increment batch counter
6. **Cleanup**: Remove temp directory → restart Photos every 5 batches

### Date Extraction Priority

1. **Folder Structure**: YYYY/MM/DD path pattern
2. **Filename Patterns**: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, WP_YYYYMMDD
3. **EXIF Data**: DateTimeOriginal, CreateDate, ModifyDate (using exiftool)
4. **Metadata Files**: Associated .json, .xml, .txt files
5. **Fallback**: Uses oldest date found from all sources

### Batch Processing Logic

- Default batch size: 50GB (configurable in import_large_archive.sh)
- Folders processed individually but batched for import efficiency
- Photos app restarted every 5 batches to prevent memory leaks
- Progress tracking separates batch counter from folder processing state
- Atomic JSON updates using temp files to prevent corruption

### Duplicate Detection

- **Content-based**: SHA-256 hash computed for each file
- **Tracking**: dupe_files array in import_progress.json
- **Skip-on-import**: osxphotos --skip-dups flag provides secondary protection
- **Importance**: Critical for large archives where same files may exist in multiple folders

## Key Commands

### Environment Setup
```bash
# Install dependencies and create virtual environment
./setup_import.sh

# Activate virtual environment (REQUIRED before running Python scripts)
source ./venv/bin/activate
```

### Import Operations
```bash
# Start import
./import_large_archive.sh

# Check status
python3 import_status.py status

# View logs
python3 import_status.py logs
python3 import_status.py logs --lines 100

# Manage import
python3 import_status.py pause
python3 import_status.py resume
python3 import_status.py reset  # ⚠️ Destructive - backs up progress file
```

### Index Management
```bash
# View index statistics
./index_stats.sh

# Force rebuild index (after adding new photos)
./reindex.sh
```

## Critical Implementation Details

### Dependencies
- **macOS-specific**: Uses AppleScript (osascript) to control Photos app
- **SMB share required**: Mounted at `/Volumes/SlowDisk` (configured for optimized performance)
- **Homebrew packages**: `exiftool`, `jq` (installed via setup_import.sh)
- **Python packages**: `Pillow>=10.0.0`, `PyExifTool>=0.5.5`, `osxphotos>=0.74.0`

### Unicode/International Character Handling
- All scripts set `LC_ALL=en_US.UTF-8` and `LANG=en_US.UTF-8`
- Critical for reliably processing files with non-ASCII characters
- Applies to both bash scripts and Python modules

### Error Recovery
- Each folder processed independently → failure doesn't stop entire batch
- Automatic retry (3 attempts) with Photos app restart between attempts
- Failed files tracked in import_progress.json failed_files array
- Interruption (SIGINT/SIGTERM) triggers graceful cleanup and status update

### Disk Space Management
- Pre-flight check requires 10GB free space
- Each 50GB batch temporarily copied before import (doubles space requirement)
- Temp directory cleaned immediately after successful import
- Failed batches retain temp directory for debugging

### Resumability Design
- **Atomic updates**: All JSON writes use temp file + atomic mv
- **Cross-PC support**: Tracking on SMB share allows resuming from different machines
- **Progress display**: import_large_archive.sh shows previous progress on start
- **Validation**: Scripts verify index validity and rebuild if corrupted

## Code Organization Patterns

### Bash Scripts
- Use `set -euo pipefail` for error handling
- Color-coded logging: GREEN (info), YELLOW (warn), RED (error)
- Functions for modularity and testability
- All external dependencies checked before execution

### Python Modules
- Top-level functions for bash interoperability (can be called via python3 -c)
- Clear separation: extract_date_* functions, each with specific pattern matching
- Logging to stdout/stderr (not files) for bash pipeline integration
- No direct file writes in date_fixer.py (returns data or copies to temp)

### Configuration
- Batch size: `BATCH_SIZE_GB` variable in import_large_archive.sh
- Source directory: `SOURCE_DIR` variable (currently hardcoded)
- Album name: `ALBUM_NAME` variable (default: "import2025")
- All configurable at top of import_large_archive.sh

## Testing Considerations

The `test_setup.py` script checks the environment (no unit tests exist). When modifying code:
- Test with small subset of files first
- Check json file validity after modifications
- Verify unicode character handling with international filenames
- Monitor /Volumes/SlowDisk/iCloud/import_log.txt for detailed error info
