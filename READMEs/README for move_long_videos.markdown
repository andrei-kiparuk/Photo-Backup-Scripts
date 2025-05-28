# Move Long Videos Script

## Description
This Bash script moves video files longer than a specified duration (e.g., 5 minutes) to a destination folder, organizing them into `YYYY/MM/DD` folders based on file dates. It uses `ffprobe` to check video duration.

## Prerequisites
- **Operating System**: macOS or Linux
- **Dependencies**:
  - `ffmpeg`: Install via Homebrew (`brew install ffmpeg`) on macOS
- **Folders**:
  - Source: `/Volumes/T7/to import` (read access)
  - Destination: `/Volumes/T7/long_videos` (write access)
- **Permissions**: Read/write access to both folders

## Usage
Run the script, specifying the source folder and minimum duration (in seconds).

### Command
```bash
./move_long_videos.sh /Volumes/T7/to import 300
```

### Parameters
- `/path/to/source`: Path to the folder with videos (default: `/Volumes/T7/to import`)
- `duration`: Minimum video duration in seconds (default: 300)

### Supported File Extensions
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.m4v`

### Example
```bash
./move_long_videos.sh /Volumes/T7/to import 300
```
Moves `video.mp4` (6 minutes) to `/Volumes/T7/long_videos/2023/05/27/video.mp4`.

## Notes
- **Duration Check**: Uses `ffprobe` to accurately determine video length.
- **Backup**: Back up files before running.
- **Error Handling**: Skips invalid or short videos; logs to console.