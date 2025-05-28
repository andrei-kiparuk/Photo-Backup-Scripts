# Photo-Backup-Scripts

## Overview
This repository contains a collection of scripts designed to manage, process, and organize photo and video files. The scripts facilitate tasks such as exporting/importing media to/from the macOS Photos app, converting file formats (e.g., to HEIC/HEVC), organizing files into `YYYY/MM/DD` folder structures, applying metadata, and handling Google Takeout exports. They are primarily developed for macOS but include Windows-compatible scripts for cross-platform use.

## General Purpose of Scripts
The scripts serve various media management needs, including:
- **Exporting/Importing Media**: Transfer photos and videos to/from the macOS Photos app, with support for iCloud syncing and metadata preservation.
- **File Conversion**: Convert images and videos to efficient formats like HEIC and HEVC, optimized for Apple devices or storage.
- **Metadata Management**: Apply or fix EXIF metadata using JSON files (e.g., from Google Takeout) or folder dates.
- **File Organization**: Sort media into `YYYY/MM/DD` folders based on content dates, file dates, or metadata.
- **Duplicate Removal**: Identify and remove duplicate or similar files using hashes or perceptual hashing.
- **Specialized Tasks**: Handle specific use cases like processing GoPro videos, YouTube downloads, or long-duration videos.

Supported file extensions include:
- **Photos**: `.jpg`, `.jpeg`, `.png`, `.heic`, `.heif`, `.cr2`, `.dng`, `.tiff`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`, `.wmv`, `.3gp`, `.flv`, `.mpeg`, `.vob`

## Finding Script-Specific READMEs
Each script has a dedicated `README.md` file located in the `READMEs/` directory. These files provide detailed descriptions, usage instructions, parameters, dependencies, and examples for individual scripts. The naming convention is `README_<script_name>.md`, where `<script_name>` replaces dots with underscores (e.g., `README_adjust_file_dates_py.md` for `adjust_file_dates.py`).

To find a script’s `README`:
1. Navigate to the `READMEs/` directory: `https://github.com/andrei-kiparuk/Photo-Backup-Scripts/tree/main/READMEs`.
2. Locate the file matching the script’s name (e.g., `README_export_photos_sh.md` for `export_photos.sh`).
3. Open the file for detailed documentation.

## Usage Guidance
### Prerequisites
- **Operating System**: Most scripts are designed for macOS; some (e.g., `.ps1` scripts, `convert_win.py`) support Windows.
- **Dependencies**: Common tools include:
    - `osxphotos` (`pip install osxphotos`) for macOS Photos app integration.
    - `exiftool` (`brew install exiftool` on macOS or download for Windows) for metadata handling.
    - `ffmpeg` (`brew install ffmpeg` or Windows download) for video conversion.
    - Python libraries: `pillow`, `pillow_heif`, `imagehash` (`pip install pillow pillow_heif imagehash`).
- **Folders**: Scripts often use paths like `/Volumes/T7`, `/Volumes/WDsmall/Icloud`, `/Volumes/JBOD/Converted`, or `D:\Icloud` (Windows). Update paths in scripts as needed.
- **Permissions**: Ensure read/write access to source/destination folders and Photos app access (macOS).

### Recommendations
- **Backup**: Always back up media files and the Photos library (e.g., via Time Machine) before running scripts, as some modify or delete files.
- **Test**: Run scripts on a small dataset first to verify behavior.
- **Dependencies**: Install required tools and verify they’re in your system PATH.
- **Script Selection**: Review the `READMEs/` directory to choose the script best suited for your task (e.g., `convert_takeout_mac.py` for Google Takeout on macOS).

## Getting Started
1. Clone the repository: `git clone https://github.com/andrei-kiparuk/Photo-Backup-Scripts.git`.
2. Install dependencies based on the script’s `README` (see `READMEs/`).
3. Update script paths to match your environment (e.g., external drive mounts).
4. Run the desired script with appropriate parameters, as detailed in its `README`.

For questions or contributions, open an issue or pull request on GitHub.