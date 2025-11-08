#!/usr/bin/env python3
"""
Visual Duplicate Finder
Detects duplicate photos and videos by visual content (perceptual hashing)
Preserves the oldest file with maximum EXIF/metadata information

Features:
- Perceptual hashing for visual similarity detection
- Metadata scoring to keep the richest file
- Date-aware comparison (only within same YYYY/MM/DD folders)
- Two search modes: all folders or deepest folders only
- Preserves folder structure when moving duplicates
"""

import os
import sys
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
import logging
from collections import defaultdict

# Image and video processing
from PIL import Image
import imagehash
import numpy as np

# Metadata extraction
import exiftool

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable HEIC support for Pillow (must be after logger is defined)
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    logger.info("HEIC support enabled via pillow-heif")
except ImportError:
    logger.warning("pillow-heif not available. HEIC files will use fallback hashing.")

# Supported file extensions
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.tif',
    '.bmp', '.gif', '.webp', '.cr2', '.nef', '.arw', '.dng', '.raw'
}

VIDEO_EXTENSIONS = {
    '.mp4', '.mov', '.avi', '.mkv', '.m4v', '.wmv', '.flv', '.3gp', '.mts', '.mpg', '.mpeg'
}

ALL_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


class VisualDuplicateFinder:
    def __init__(self, archive_path: str, duplicates_path: str, search_mode: str):
        """
        Initialize the duplicate finder

        Args:
            archive_path: Path to photo/video archive
            duplicates_path: Path where duplicates will be moved
            search_mode: 'all' or 'deepest' - search mode
        """
        self.archive_path = Path(archive_path).resolve()
        self.duplicates_path = Path(duplicates_path).resolve()
        self.search_mode = search_mode

        # Hash database: {date_key: {hash_value: [file_info]}}
        self.hash_db: Dict[str, Dict[str, List[Dict]]] = defaultdict(lambda: defaultdict(list))

        # Statistics
        self.stats = {
            'total_files_scanned': 0,
            'duplicates_found': 0,
            'files_moved': 0,
            'errors': 0
        }

        # Ensure duplicates directory exists
        self.duplicates_path.mkdir(parents=True, exist_ok=True)

    def extract_date_from_path(self, file_path: Path) -> Optional[str]:
        """
        Extract date key (YYYY/MM/DD) from file path

        Args:
            file_path: Path to file

        Returns:
            Date key as "YYYY/MM/DD" or None if not found
        """
        try:
            path_parts = file_path.parts
            for i, part in enumerate(path_parts):
                # Look for YYYY/MM/DD pattern
                if re.match(r'^\d{4}$', part):
                    if i + 2 < len(path_parts):
                        year = part
                        month = path_parts[i + 1]
                        day = path_parts[i + 2]

                        # Validate month and day
                        if (re.match(r'^\d{2}$', month) and
                            re.match(r'^\d{2}$', day)):
                            # Validate ranges
                            month_int = int(month)
                            day_int = int(day)
                            if 1 <= month_int <= 12 and 1 <= day_int <= 31:
                                return f"{year}/{month}/{day}"
        except Exception as e:
            logger.warning(f"Could not extract date from {file_path}: {e}")

        return None

    def get_perceptual_hash(self, file_path: Path) -> Optional[str]:
        """
        Calculate perceptual hash for image or video file

        Args:
            file_path: Path to image or video file

        Returns:
            Perceptual hash as string, or None if failed
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return None

            ext = file_path.suffix.lower()

            if ext in IMAGE_EXTENSIONS:
                # For images, calculate perceptual hash directly
                try:
                    with Image.open(file_path) as img:
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')

                        # Calculate phash (perceptual hash)
                        hash_value = imagehash.phash(img)
                        return str(hash_value)
                except Exception as e:
                    logger.warning(f"Cannot open image file {file_path} with PIL: {e}")
                    # Fallback: use file characteristics
                    stat = file_path.stat()
                    return f"image_fallback:{stat.st_size}:{int(stat.st_mtime)}:{ext}"

            elif ext in VIDEO_EXTENSIONS:
                # For videos, hash the first frame as representative
                # This is a simplification - in production you might want to hash multiple frames
                try:
                    # Try to extract first frame using ffmpeg if available
                    import subprocess
                    import tempfile

                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_frame:
                        temp_frame_path = temp_frame.name

                        # Extract first frame using ffmpeg
                        cmd = [
                            'ffmpeg', '-i', str(file_path),
                            '-vf', 'scale=320:240',
                            '-vframes', '1',
                            '-f', 'image2',
                            temp_frame_path,
                            '-y', '-loglevel', 'error'
                        ]

                        result = subprocess.run(cmd, capture_output=True)

                        if result.returncode == 0 and os.path.exists(temp_frame_path):
                            # Hash the extracted frame
                            with Image.open(temp_frame_path) as img:
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                hash_value = imagehash.phash(img)
                                frame_hash = str(hash_value)

                            # Clean up
                            os.unlink(temp_frame_path)
                            return f"video_frame:{frame_hash}"
                        else:
                            # If ffmpeg fails, use file size and modification time as fallback
                            stat = file_path.stat()
                            fallback_hash = f"video_fallback:{stat.st_size}:{int(stat.st_mtime)}"
                            logger.warning(f"Could not extract frame from {file_path}, using fallback hash")
                            return fallback_hash

                except Exception as e:
                    logger.warning(f"Video processing failed for {file_path}: {e}")
                    # Fallback for videos
                    stat = file_path.stat()
                    return f"video_fallback:{stat.st_size}:{int(stat.st_mtime)}"

            else:
                logger.warning(f"Unsupported file type: {ext}")
                return None

        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            self.stats['errors'] += 1
            return None

    def get_metadata_score(self, file_path: Path) -> Tuple[int, Dict]:
        """
        Calculate metadata richness score for a file

        Args:
            file_path: Path to file

        Returns:
            Tuple of (score, metadata_dict)
        """
        metadata = {}
        score = 0

        try:
            with exiftool.ExifTool() as et:
                # Execute exiftool and get JSON output
                metadata_list = et.execute_json(str(file_path))

                if not metadata_list or len(metadata_list) == 0:
                    return 0, {}

                # Get the first (and only) metadata dictionary
                metadata = metadata_list[0]

                # Score based on EXIF fields present
                exif_fields = [
                    'EXIF:DateTimeOriginal',      # Original capture time
                    'EXIF:CreateDate',             # Creation date
                    'EXIF:ModifyDate',             # Modification date
                    'EXIF:Make', 'EXIF:Model',     # Camera info
                    'EXIF:ImageWidth', 'EXIF:ImageHeight',  # Dimensions
                    'EXIF:Orientation',            # Orientation
                    'EXIF:Flash',                  # Flash info
                    'EXIF:FocalLength',            # Focal length
                    'EXIF:ISO',                    # ISO
                    'EXIF:Aperture', 'EXIF:FNumber',  # Aperture
                    'EXIF:ExposureTime',           # Exposure
                    'EXIF:WhiteBalance',           # White balance
                    'EXIF:GPSLatitude', 'EXIF:GPSLongitude',  # GPS
                    'IPTC:Keywords',               # Tags/keywords
                    'XMP:Subject',                 # XMP tags
                    'QuickTime:CreateDate',        # Video creation date
                    'QuickTime:Model',             # Video camera model
                ]

                # Complex scoring: more important fields get higher weight
                weights = {
                    'EXIF:DateTimeOriginal': 10,
                    'EXIF:CreateDate': 8,
                    'EXIF:GPSLatitude': 7,
                    'EXIF:GPSLongitude': 7,
                    'IPTC:Keywords': 5,
                    'XMP:Subject': 5,
                    'EXIF:Make': 3,
                    'EXIF:Model': 3,
                    'EXIF:FocalLength': 2,
                    'EXIF:ISO': 2,
                    'EXIF:Flash': 2,
                    'EXIF:Orientation': 2
                }

                for field in exif_fields:
                    if field in metadata and metadata[field]:
                        score += weights.get(field, 1)

                # Bonus for having GPS coordinates
                if 'EXIF:GPSLatitude' in metadata and 'EXIF:GPSLongitude' in metadata:
                    score += 5

                # Bonus for having tags/keywords
                if ('IPTC:Keywords' in metadata and metadata['IPTC:Keywords']) or \
                   ('XMP:Subject' in metadata and metadata['XMP:Subject']):
                    score += 3

        except Exception as e:
            logger.warning(f"Could not extract metadata from {file_path}: {e}")

        return score, metadata

    def get_file_age(self, file_path: Path) -> datetime:
        """
        Get file age based on EXIF date or file modification time

        Args:
            file_path: Path to file

        Returns:
            datetime object representing file age
        """
        try:
            # Try to get date from EXIF first
            with exiftool.ExifTool() as et:
                metadata_list = et.execute_json(str(file_path))

                if metadata_list and len(metadata_list) > 0:
                    metadata = metadata_list[0]

                    # Prefer DateTimeOriginal, then CreateDate, then modification time
                    date_fields = ['EXIF:DateTimeOriginal', 'EXIF:CreateDate', 'QuickTime:CreateDate']
                    for field in date_fields:
                        if field in metadata and metadata[field]:
                            try:
                                date_str = metadata[field]
                                # Parse various date formats
                                for fmt in ['%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y:%m:%d']:
                                    try:
                                        return datetime.strptime(date_str, fmt)
                                    except:
                                        continue
                            except:
                                continue

        except Exception as e:
            logger.warning(f"Could not extract date from EXIF for {file_path}: {e}")

        # Fall back to file modification time
        return datetime.fromtimestamp(file_path.stat().st_mtime)

    def is_deepest_folder(self, folder_path: Path) -> bool:
        """
        Check if a folder is a "deepest" folder (contains files but no subfolders with media)

        Args:
            folder_path: Path to folder

        Returns:
            True if this is a deepest folder
        """
        try:
            # Check if any subdirectories contain media files
            for item in folder_path.iterdir():
                if item.is_dir():
                    # Check if this subdirectory or its children have media files
                    for root, _, files in os.walk(item):
                        for file in files:
                            if Path(file).suffix.lower() in ALL_EXTENSIONS:
                                return False
            return True
        except:
            return False

    def scan_files(self):
        """
        Scan all files in the archive and build hash database
        """
        logger.info(f"Scanning files in {self.archive_path}")
        logger.info(f"Search mode: {self.search_mode}")
        logger.info(f"Duplicates will be moved to: {self.duplicates_path}")

        # Walk through directory tree
        for root, dirs, files in os.walk(self.archive_path):
            root_path = Path(root)

            # Skip if in deepest mode and this is not a deepest folder
            if self.search_mode == 'deepest' and not self.is_deepest_folder(root_path):
                continue

            # Process files in this folder
            for file in files:
                file_path = root_path / file
                ext = file_path.suffix.lower()

                # Skip if not a supported media file
                if ext not in ALL_EXTENSIONS:
                    continue

                # Extract date from path
                date_key = self.extract_date_from_path(file_path)
                if not date_key:
                    logger.warning(f"Could not extract date from path: {file_path}")
                    continue

                # Calculate perceptual hash
                hash_value = self.get_perceptual_hash(file_path)
                if not hash_value:
                    continue

                # Get metadata score
                score, metadata = self.get_metadata_score(file_path)

                # Get file age (with a try-except in case of errors)
                try:
                    file_age = self.get_file_age(file_path)
                except Exception as e:
                    logger.warning(f"Could not get file age for {file_path}: {e}")
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)

                # Store file info
                file_info = {
                    'path': str(file_path),
                    'hash': hash_value,
                    'metadata_score': score,
                    'metadata': metadata,
                    'file_age': file_age.isoformat(),
                    'size': file_path.stat().st_size
                }

                # Add to hash database
                self.hash_db[date_key][hash_value].append(file_info)

                self.stats['total_files_scanned'] += 1

                # Progress indicator
                if self.stats['total_files_scanned'] % 100 == 0:
                    logger.info(f"Scanned {self.stats['total_files_scanned']} files...")

        logger.info(f"Scan complete. Processed {self.stats['total_files_scanned']} files.")

    def find_duplicates(self) -> List[Tuple[str, List[Dict]]]:
        """
        Find all duplicate groups

        Returns:
            List of tuples: (date_key, list_of_duplicate_files)
        """
        duplicates = []

        for date_key, hash_groups in self.hash_db.items():
            for hash_value, file_list in hash_groups.items():
                if len(file_list) > 1:
                    # Found duplicates
                    duplicates.append((date_key, file_list))
                    self.stats['duplicates_found'] += len(file_list) - 1

        return duplicates

    def select_file_to_keep(self, file_list: List[Dict]) -> Tuple[str, List[str]]:
        """
        Select which file to keep based on metadata score and age
        Priority: Highest metadata score, then oldest file

        Args:
            file_list: List of file info dictionaries

        Returns:
            Tuple of (file_to_keep, list_of_duplicates_to_move)
        """
        # Sort by metadata score (descending), then by file age (ascending = older first)
        sorted_files = sorted(
            file_list,
            key=lambda x: (x['metadata_score'], -datetime.fromisoformat(x['file_age']).timestamp()),
            reverse=True
        )

        # Keep the first file (best score, oldest if tie)
        keep_file = sorted_files[0]['path']

        # Rest are duplicates to move
        duplicates_to_move = [f['path'] for f in sorted_files[1:]]

        return keep_file, duplicates_to_move

    def get_relative_path(self, file_path: str) -> Path:
        """
        Get path relative to archive root

        Args:
            file_path: Full file path

        Returns:
            Relative path from archive root
        """
        full_path = Path(file_path).resolve()
        try:
            return full_path.relative_to(self.archive_path)
        except ValueError:
            # If relative path can't be determined, use the full path
            return Path(file_path)

    def move_file_to_duplicates(self, file_path: str):
        """
        Move a file to duplicates folder, preserving folder structure

        Args:
            file_path: Path to file to move
        """
        try:
            src_path = Path(file_path)
            rel_path = self.get_relative_path(file_path)
            dest_path = self.duplicates_path / rel_path

            # Create destination directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            shutil.move(str(src_path), str(dest_path))

            logger.info(f"Moved duplicate: {src_path} -> {dest_path}")
            self.stats['files_moved'] += 1

        except Exception as e:
            logger.error(f"Failed to move {file_path}: {e}")
            self.stats['errors'] += 1

    def process_duplicates(self):
        """
        Find and process all duplicates
        """
        logger.info("Finding duplicates...")
        duplicate_groups = self.find_duplicates()

        if not duplicate_groups:
            logger.info("No duplicates found!")
            return

        logger.info(f"Found {len(duplicate_groups)} groups of duplicates")
        logger.info(f"Total duplicate files: {self.stats['duplicates_found']}")

        # Process each duplicate group
        for date_key, file_list in duplicate_groups:
            logger.info(f"\nProcessing duplicates for {date_key}")

            # Show all files in this group
            logger.info(f"  Found {len(file_list)} similar files:")
            for f in file_list:
                logger.info(f"    - {Path(f['path']).name} (score: {f['metadata_score']})")

            # Select which file to keep
            keep_file, duplicates_to_move = self.select_file_to_keep(file_list)

            logger.info(f"  Keeping: {Path(keep_file).name}")

            # Move duplicates
            for dup_file in duplicates_to_move:
                self.move_file_to_duplicates(dup_file)

        # Final statistics
        logger.info("\n" + "="*50)
        logger.info("PROCESSING COMPLETE")
        logger.info("="*50)
        logger.info(f"Total files scanned: {self.stats['total_files_scanned']}")
        logger.info(f"Duplicate groups found: {len(duplicate_groups)}")
        logger.info(f"Duplicate files moved: {self.stats['files_moved']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Duplicates folder: {self.duplicates_path}")

    def save_report(self):
        """
        Save detailed report to JSON file
        """
        report_file = self.duplicates_path / "duplicate_report.json"

        report = {
            'scan_info': {
                'archive_path': str(self.archive_path),
                'duplicates_path': str(self.duplicates_path),
                'search_mode': self.search_mode,
                'scan_date': datetime.now().isoformat()
            },
            'statistics': self.stats,
            'duplicates': []
        }

        # Add duplicate groups
        for date_key, file_list in self.find_duplicates():
            keep_file, duplicates_to_move = self.select_file_to_keep(file_list)

            report['duplicates'].append({
                'date': date_key,
                'files': file_list,
                'kept_file': keep_file,
                'moved_files': duplicates_to_move
            })

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\nDetailed report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Find visual duplicates in photo/video archive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search all folders recursively
  python visual_duplicate_finder.py /path/to/archive all

  # Search only deepest folders (day-level YYYY/MM/DD)
  python visual_duplicate_finder.py /path/to/archive deepest

  # Custom duplicates folder location
  python visual_duplicate_finder.py /path/to/archive all --duplicates /path/to/duplicates
        """
    )

    parser.add_argument('archive_path',
                       help='Path to photo/video archive')

    parser.add_argument('search_mode',
                       choices=['all', 'deepest'],
                       help="Search mode: 'all' folders or only 'deepest' folders")

    parser.add_argument('--duplicates', '-d',
                       default=None,
                       help='Path where duplicates will be moved (default: archive_path/../duplicates)')

    parser.add_argument('--log-level', '-l',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO',
                       help='Logging level (default: INFO)')

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Validate archive path
    archive_path = Path(args.archive_path)
    if not archive_path.exists():
        logger.error(f"Archive path does not exist: {archive_path}")
        sys.exit(1)

    if not archive_path.is_dir():
        logger.error(f"Archive path is not a directory: {archive_path}")
        sys.exit(1)

    # Set duplicates path
    if args.duplicates:
        duplicates_path = Path(args.duplicates)
    else:
        duplicates_path = archive_path.parent / 'duplicates'

    logger.info("="*60)
    logger.info("Visual Duplicate Finder")
    logger.info("="*60)
    logger.info(f"Archive: {archive_path}")
    logger.info(f"Search mode: {args.search_mode}")
    logger.info(f"Duplicates folder: {duplicates_path}")
    logger.info("="*60)

    # Create finder and run
    finder = VisualDuplicateFinder(
        archive_path=str(archive_path),
        duplicates_path=str(duplicates_path),
        search_mode=args.search_mode
    )

    # Scan files
    finder.scan_files()

    # Process duplicates
    finder.process_duplicates()

    # Save report
    finder.save_report()

    logger.info("\nDone!")


if __name__ == '__main__':
    import re
    main()
