# Visual Duplicate Finder - Quick Reference

## Installation

```bash
# Install dependencies (includes ImageHash and numpy)
./setup_import.sh
```

## Basic Usage

```bash
# Search all folders recursively
./run_duplicate_finder.sh /path/to/archive all

# Search only deepest folders (day-level YYYY/MM/DD) - RECOMMENDED
./run_duplicate_finder.sh /path/to/archive deepest
```

## Command Structure

```
./run_duplicate_finder.sh <archive_path> <search_mode> [options]
```

### Required Arguments

- `<archive_path>`: Path to photo/video archive
- `<search_mode>`: Either `all` or `deepest`
  - `all`: Search through all folders and subfolders
  - `deepest`: Only search in deepest folders (day-level YYYY/MM/DD)

### Optional Arguments

- `--duplicates PATH`: Custom location for duplicates (default: archive/../duplicates)
- `--log-level LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR)

## Examples

```bash
# Example 1: Basic usage with default duplicates folder
./run_duplicate_finder.sh /Volumes/SlowDisk/iCloud deepest

# Example 2: Custom duplicates location
./run_duplicate_finder.sh /Users/akiparuk/Pictures all \
  --duplicates /Users/akiparuk/Desktop/duplicates

# Example 3: Debug mode for troubleshooting
./run_duplicate_finder.sh /Volumes/SlowDisk/iCloud deepest \
  --log-level DEBUG

# Example 4: Dry run (check what would happen without --log-level)
./run_duplicate_finder.sh /Volumes/SlowDisk/iCloud deepest \
  --log-level INFO
```

## Understanding the Output

### During Scan

```
[2025-01-07 10:30:15] Scanning files in /Volumes/SlowDisk/iCloud
[2025-01-07 10:30:15] Search mode: deepest
[2025-01-07 10:30:15] Duplicates will be moved to: /Volumes/SlowDisk/duplicates
[2025-01-07 10:30:25] Scanned 100 files...
[2025-01-07 10:30:35] Scanned 200 files...
[2025-01-07 10:30:45] Scan complete. Processed 250 files.
```

### Duplicate Detection

```
[2025-01-07 10:30:50] Processing duplicates for 2020/01/15
[2025-01-07 10:30:50]   Found 3 similar files:
[2025-01-07 10:30:50]     - IMG_1234.jpg (score: 45)
[2025-01-07 10:30:50]     - IMG_1234_copy.jpg (score: 12)
[2025-01-07 10:30:50]     - IMG_1234_edited.jpg (score: 28)
[2025-01-07 10:30:50]   Keeping: IMG_1234.jpg
[2025-01-07 10:30:50] Moved duplicate: /Volumes/SlowDisk/iCloud/2020/01/15/IMG_1234_copy.jpg -> /Volumes/SlowDisk/duplicates/2020/01/15/IMG_1234_copy.jpg
[2025-01-07 10:30:50] Moved duplicate: /Volumes/SlowDisk/iCloud/2020/01/15/IMG_1234_edited.jpg -> /Volumes/SlowDisk/duplicates/2020/01/15/IMG_1234_edited.jpg
```

### Summary

```
==================================================
PROCESSING COMPLETE
==================================================
Total files scanned: 15247
Duplicate groups found: 342
Duplicate files moved: 856
Errors: 0
Duplicates folder: /Volumes/SlowDisk/duplicates

Detailed report saved to: /Volumes/SlowDisk/duplicates/duplicate_report.json
```

## Metadata Scoring System

Files are scored based on EXIF/metadata richness:

| Field Type | Points | Examples |
|------------|--------|----------|
| Capture Date/Time | 10 | DateTimeOriginal |
| Creation Date | 8 | CreateDate |
| GPS Coordinates | 7 | GPSLatitude, GPSLongitude |
| Keywords/Tags | 5 | IPTC:Keywords, XMP:Subject |
| Camera Info | 3 | Make, Model |
| Technical Details | 2 | FocalLength, ISO, Flash, Orientation |
| Other EXIF | 1 | Various fields |

**Selection Priority:**
1. Highest metadata score (most information)
2. If tied, oldest file (based on EXIF date or modification time)

## Archive Structure Requirements

Expected folder structure:
```
/Volumes/SlowDisk/iCloud/
├── 2020/
│   ├── 01/
│   │   ├── 01/     # January 1st
│   │   │   ├── photo1.jpg
│   │   │   └── photo2.mov
│   │   └── 15/     # January 15th
│   └── 12/
└── 2021/
```

The script only compares files within the same date folder (e.g., only compares files in 2020/01/15 with other files in 2020/01/15).

## Understanding Search Modes

### Mode: `deepest` (RECOMMENDED)

Only searches in the deepest folder level (day folders). **Best for YYYY/MM/DD structure.**

**Pros:**
- Faster (skips intermediate folders)
- Correct for date-based archives
- Only compares files from the same day

**Use when:**
- Your photos are organized by date (YYYY/MM/DD)
- You want to deduplicate within each day only

### Mode: `all`

Searches through ALL folders and subfolders recursively.

**Pros:**
- Comprehensive search
- Finds duplicates anywhere in the structure

**Cons:**
- Slower
- May find duplicates across different dates (which are then filtered out by date-aware logic)

**Use when:**
- You have non-date-based organization
- You want to scan every folder

## After Running

1. **Check duplicates folder**: Verify files were moved correctly
2. **Review report**: Check `duplicates/duplicate_report.json` for details
3. **Delete or archive**: Delete duplicates folder or move to long-term archive
4. **Run import**: If preparing for Photos import, run `./import_large_archive.sh`

## Troubleshooting

### FFmpeg Not Found (for videos)

Better video hashing requires ffmpeg. To install:
```bash
brew install ffmpeg
```

If ffmpeg is not available, the script uses fallback hashing (file size + modification time).

### Permission Errors

If you get "Permission denied" errors:
```bash
chmod +x visual_duplicate_finder.py run_duplicate_finder.sh
```

### Virtual Environment Not Found

```bash
# Run setup if venv doesn't exist
./setup_import.sh
```

### Low Memory

For very large archives, you may need to:
- Close other applications
- Process in batches by year
- Use `--log-level WARNING` to reduce output

### Can't Extract Date from Path

Ensure your folder structure follows YYYY/MM/DD format. The script will skip files that don't match this pattern.

## Example Workflow

1. **Setup** (if first time):
   ```bash
   ./setup_import.sh
   ```

2. **Find duplicates**:
   ```bash
   ./run_duplicate_finder.sh /Volumes/SlowDisk/iCloud deepest
   ```

3. **Review duplicates**:
   ```bash
   # Check the duplicates folder
   open /Volumes/SlowDisk/duplicates

   # Review the report
   cat /Volumes/SlowDisk/duplicates/duplicate_report.json | jq
   ```

4. **Import to Photos**:
   ```bash
   ./import_large_archive.sh
   ```

## Tips

- **Always backup first**: This script moves files permanently
- **Test on small subset**: Copy a few folders to test before running on entire archive
- **Use deepest mode**: Much faster for date-based archives
- **Check report**: Always review the JSON report before deleting duplicates folder
- **Monitor progress**: Use `--log-level INFO` to see what's happening

## Supported File Types

**Images:** JPG, JPEG, PNG, HEIC, HEIF, TIFF, TIF, BMP, GIF, WebP, CR2, NEF, ARW, DNG, RAW

**Videos:** MP4, MOV, AVI, MKV, M4V, WMV, FLV, 3GP, MTS, MPG, MPEG
