#!/usr/bin/env python3
"""
Date Fixer for Large Photo Archive Import
Handles date extraction from folder structure, EXIF data, and metadata files
"""

import os
import sys
import shutil
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import exiftool
from PIL import Image
from PIL.ExifTags import TAGS
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif', '.tiff', '.tif',
    '.cr2', '.nef', '.arw', '.dng', '.raw',
    '.mp4', '.mov', '.avi', '.mkv', '.m4v', '.3gp'
}

# Metadata file extensions
METADATA_EXTENSIONS = {'.json', '.xml', '.txt'}

class DateFixer:
    def __init__(self, source_dir: str, temp_dir: str):
        self.source_dir = Path(source_dir)
        self.temp_dir = Path(temp_dir)
        self.processed_files = 0
        self.duplicate_files = []
        
    def extract_date_from_folder_path(self, file_path: Path) -> Optional[datetime]:
        """Extract date from folder structure YYYY/MM/DD"""
        try:
            # Look for YYYY/MM/DD pattern in the path
            path_parts = file_path.parts
            for i, part in enumerate(path_parts):
                if re.match(r'^\d{4}$', part):  # Year
                    if i + 2 < len(path_parts):
                        month_part = path_parts[i + 1]
                        day_part = path_parts[i + 2]
                        if (re.match(r'^\d{2}$', month_part) and 
                            re.match(r'^\d{2}$', day_part)):
                            year = int(part)
                            month = int(month_part)
                            day = int(day_part)
                            if (1900 <= year <= 2030 and 
                                1 <= month <= 12 and 
                                1 <= day <= 31):
                                return datetime(year, month, day, 12, 0, 0)
        except (ValueError, IndexError):
            pass
        return None
    
    def extract_date_from_filename(self, filename: str) -> Optional[datetime]:
        """Extract date from filename patterns"""
        patterns = [
            # YYYY-MM-DD
            r'(\d{4})-(\d{2})-(\d{2})',
            # YYYY_MM_DD
            r'(\d{4})_(\d{2})_(\d{2})',
            # YYYYMMDD
            r'(\d{4})(\d{2})(\d{2})',
            # WP_YYYYMMDD
            r'WP_(\d{4})(\d{2})(\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    if pattern.startswith('WP_'):
                        year, month, day = match.groups()
                    else:
                        year, month, day = match.groups()
                    
                    year, month, day = int(year), int(month), int(day)
                    if (1900 <= year <= 2030 and 
                        1 <= month <= 12 and 
                        1 <= day <= 31):
                        return datetime(year, month, day, 12, 0, 0)
                except (ValueError, IndexError):
                    continue
        return None
    
    def extract_date_from_exif(self, file_path: Path) -> Optional[datetime]:
        """Extract date from EXIF metadata"""
        try:
            with exiftool.ExifToolHelper() as et:
                metadata = et.get_metadata(str(file_path))[0]
                
                # Priority order for date extraction
                date_tags = [
                    'EXIF:DateTimeOriginal',
                    'EXIF:CreateDate',
                    'EXIF:ModifyDate',
                    'QuickTime:CreateDate',
                    'QuickTime:ModifyDate',
                    'File:FileModifyDate',
                    'File:FileCreateDate',
                ]
                
                for tag in date_tags:
                    if tag in metadata:
                        date_str = metadata[tag]
                        parsed_date = self.parse_date_string(date_str)
                        if parsed_date:
                            return parsed_date
        except Exception as e:
            logger.debug(f"Failed to extract EXIF date from {file_path}: {e}")
        
        return None
    
    def parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats"""
        if not date_str:
            return None
            
        # Remove timezone info if present
        if '+' in date_str or '-' in date_str[-6:]:
            date_str = date_str[:-6]
        
        # Remove sub-second precision
        if '.' in date_str and date_str.count(':') >= 2:
            date_str = date_str.split('.')[0]
        
        # Try various date formats
        formats = [
            '%Y:%m:%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def extract_date_from_metadata_file(self, file_path: Path) -> Optional[datetime]:
        """Extract date from associated metadata files"""
        base_path = file_path.with_suffix('')
        
        for ext in METADATA_EXTENSIONS:
            metadata_file = base_path.with_suffix(ext)
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Try to parse as JSON
                    try:
                        data = json.loads(content)
                        # Look for common date fields
                        date_fields = ['date', 'created', 'timestamp', 'time']
                        for field in date_fields:
                            if field in data:
                                date_str = str(data[field])
                                parsed_date = self.parse_date_string(date_str)
                                if parsed_date:
                                    return parsed_date
                    except json.JSONDecodeError:
                        # Try to find date patterns in text
                        date_patterns = [
                            r'(\d{4})-(\d{2})-(\d{2})',
                            r'(\d{4})/(\d{2})/(\d{2})',
                        ]
                        for pattern in date_patterns:
                            match = re.search(pattern, content)
                            if match:
                                year, month, day = map(int, match.groups())
                                if (1900 <= year <= 2030 and 
                                    1 <= month <= 12 and 
                                    1 <= day <= 31):
                                    return datetime(year, month, day, 12, 0, 0)
                except Exception as e:
                    logger.debug(f"Failed to read metadata file {metadata_file}: {e}")
        
        return None
    
    def get_oldest_date(self, file_path: Path) -> Optional[datetime]:
        """Get the oldest date from all available sources"""
        dates = []
        
        # Extract date from folder path
        folder_date = self.extract_date_from_folder_path(file_path)
        if folder_date:
            dates.append(folder_date)
        
        # Extract date from filename
        filename_date = self.extract_date_from_filename(file_path.name)
        if filename_date:
            dates.append(filename_date)
        
        # Extract date from EXIF
        exif_date = self.extract_date_from_exif(file_path)
        if exif_date:
            dates.append(exif_date)
        
        # Extract date from metadata files
        metadata_date = self.extract_date_from_metadata_file(file_path)
        if metadata_date:
            dates.append(metadata_date)
        
        if dates:
            # Return the oldest date
            return min(dates)
        
        return None
    
    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file content"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute hash for {file_path}: {e}")
            return ""
    
    def is_duplicate(self, file_path: Path, existing_hashes: Dict[str, Path]) -> bool:
        """Check if file is a duplicate based on content hash"""
        file_hash = self.compute_file_hash(file_path)
        if file_hash and file_hash in existing_hashes:
            existing_file = existing_hashes[file_hash]
            logger.info(f"Duplicate found: {file_path} matches {existing_file}")
            return True
        return False
    
    def copy_file_with_date(self, source_file: Path, target_file: Path, 
                           target_date: Optional[datetime]) -> bool:
        """Copy file to target location and set correct dates"""
        try:
            # Create target directory
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_file, target_file)
            
            # Set file dates if we have a target date
            if target_date:
                timestamp = target_date.timestamp()
                os.utime(target_file, (timestamp, timestamp))
                logger.debug(f"Set date {target_date} for {target_file}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to copy {source_file} to {target_file}: {e}")
            return False
    
    def fix_file_dates_in_folder(self, source_folder: str, temp_folder: str):
        """Process all files in a folder, fixing dates and handling duplicates"""
        source_path = Path(source_folder)
        temp_path = Path(temp_folder)
        
        if not source_path.exists():
            logger.error(f"Source folder does not exist: {source_path}")
            return
        
        # Create temp directory
        temp_path.mkdir(parents=True, exist_ok=True)
        
        # Track existing files to avoid duplicates
        existing_hashes = {}
        
        # Get all supported files
        files = []
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(source_path.rglob(f"*{ext}"))
            files.extend(source_path.rglob(f"*{ext.upper()}"))
        
        logger.info(f"Found {len(files)} files to process in {source_path}")
        
        for file_path in files:
            try:
                # Skip duplicate checking - import all files
                # if self.is_duplicate(file_path, existing_hashes):
                #     self.duplicate_files.append(str(file_path))
                #     continue
                
                # Get oldest date for this file
                oldest_date = self.get_oldest_date(file_path)
                
                # Create target path in temp directory
                relative_path = file_path.relative_to(source_path)
                target_path = temp_path / relative_path
                
                # Copy file with correct date
                if self.copy_file_with_date(file_path, target_path, oldest_date):
                    # Skip hash tracking since we're not checking duplicates
                    # file_hash = self.compute_file_hash(file_path)
                    # if file_hash:
                    #     existing_hashes[file_hash] = target_path
                    
                    self.processed_files += 1
                    
                    if self.processed_files % 100 == 0:
                        logger.info(f"Processed {self.processed_files} files...")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
        
        logger.info(f"Completed processing {self.processed_files} files")
        if self.duplicate_files:
            logger.info(f"Found {len(self.duplicate_files)} duplicate files")

def fix_file_dates_in_folder(source_folder: str, temp_folder: str):
    """Main function to fix file dates in a folder"""
    fixer = DateFixer(source_folder, temp_folder)
    fixer.fix_file_dates_in_folder(source_folder, temp_folder)
    return fixer.processed_files, fixer.duplicate_files

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 date_fixer.py <source_folder> <temp_folder>")
        sys.exit(1)
    
    source_folder = sys.argv[1]
    temp_folder = sys.argv[2]
    
    processed, duplicates = fix_file_dates_in_folder(source_folder, temp_folder)
    print(f"Processed {processed} files, found {len(duplicates)} duplicates") 