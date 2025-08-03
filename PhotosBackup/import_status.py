#!/usr/bin/env python3
"""
Import Status Checker
Provides status information and management for the large archive import process
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse

TRACKING_FILE = "/Volumes/SlowDisk/iCloud/import_progress.json"
LOG_FILE = "/Volumes/SlowDisk/iCloud/import_log.txt"

def load_progress():
    """Load progress from tracking file"""
    if not os.path.exists(TRACKING_FILE):
        return None
    
    try:
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading progress file: {e}")
        return None

def get_source_stats():
    """Get statistics about source directory"""
    source_dir = "/Volumes/SlowDisk/iCloud"
    if not os.path.exists(source_dir):
        return None
    
    total_files = 0
    total_size = 0
    folder_count = 0
    
    try:
        for root, dirs, files in os.walk(source_dir):
            # Count YYYY/MM/DD folders
            if re.match(r'.*/[0-9]{4}/[0-9]{2}/[0-9]{2}$', root):
                folder_count += 1
            
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    total_files += 1
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        print(f"Error calculating source stats: {e}")
        return None
    
    return {
        'total_files': total_files,
        'total_size_gb': total_size / (1024**3),
        'folder_count': folder_count
    }

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def show_status():
    """Show current import status"""
    progress = load_progress()
    if not progress:
        print("No progress file found. Import has not started.")
        return
    
    print("=== Import Status ===")
    print(f"Status: {progress.get('status', 'unknown')}")
    print(f"Started: {progress.get('started_at', 'unknown')}")
    print(f"Last Update: {progress.get('last_update', 'unknown')}")
    print(f"Current Batch: {progress.get('current_batch', 0)}")
    print(f"Files Processed: {progress.get('total_files_processed', 0):,}")
    print(f"Size Processed: {progress.get('total_size_processed_gb', 0):.2f} GB")
    print(f"Folders Processed: {len(progress.get('processed_folders', []))}")
    
    # Calculate progress
    source_stats = get_source_stats()
    if source_stats:
        progress_percent = (progress.get('total_files_processed', 0) / source_stats['total_files']) * 100
        size_percent = (progress.get('total_size_processed_gb', 0) / source_stats['total_size_gb']) * 100
        print(f"Progress: {progress_percent:.1f}% (files), {size_percent:.1f}% (size)")
        print(f"Remaining: {source_stats['total_files'] - progress.get('total_files_processed', 0):,} files")
        print(f"Remaining: {source_stats['total_size_gb'] - progress.get('total_size_processed_gb', 0):.2f} GB")
    
    # Calculate estimated time
    if progress.get('started_at'):
        try:
            start_time = datetime.fromisoformat(progress['started_at'].replace('Z', '+00:00'))
            if progress.get('last_update'):
                last_update = datetime.fromisoformat(progress['last_update'].replace('Z', '+00:00'))
                elapsed = (last_update - start_time).total_seconds()
                
                if progress.get('total_files_processed', 0) > 0:
                    files_per_second = progress['total_files_processed'] / elapsed
                    remaining_files = source_stats['total_files'] - progress['total_files_processed'] if source_stats else 0
                    estimated_seconds = remaining_files / files_per_second if files_per_second > 0 else 0
                    print(f"Rate: {files_per_second:.1f} files/second")
                    print(f"Estimated time remaining: {format_duration(estimated_seconds)}")
        except Exception as e:
            print(f"Error calculating time estimates: {e}")
    
    # Show recent activity
    if progress.get('last_processed_folder'):
        print(f"Last processed: {progress['last_processed_folder']}")
    
    # Show failed files
    failed_files = progress.get('failed_files', [])
    if failed_files:
        print(f"Failed files: {len(failed_files)}")
    
    # Show duplicate files
    duplicate_files = progress.get('duplicate_files', [])
    if duplicate_files:
        print(f"Duplicate files: {len(duplicate_files)}")

def show_logs(lines=50):
    """Show recent log entries"""
    if not os.path.exists(LOG_FILE):
        print("No log file found.")
        return
    
    print(f"=== Recent Logs (last {lines} lines) ===")
    try:
        with open(LOG_FILE, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            for line in recent_lines:
                print(line.rstrip())
    except Exception as e:
        print(f"Error reading log file: {e}")

def reset_progress():
    """Reset progress and start fresh"""
    if os.path.exists(TRACKING_FILE):
        backup_file = f"{TRACKING_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(TRACKING_FILE, backup_file)
        print(f"Progress file backed up to: {backup_file}")
    
    print("Progress reset. Next run will start from the beginning.")

def pause_import():
    """Pause the import process"""
    progress = load_progress()
    if not progress:
        print("No active import process found.")
        return
    
    progress['status'] = 'paused'
    progress['last_update'] = datetime.utcnow().isoformat() + 'Z'
    
    with open(TRACKING_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print("Import process paused.")

def resume_import():
    """Resume the import process"""
    progress = load_progress()
    if not progress:
        print("No progress file found.")
        return
    
    progress['status'] = 'running'
    progress['last_update'] = datetime.utcnow().isoformat() + 'Z'
    
    with open(TRACKING_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print("Import process resumed.")

def main():
    parser = argparse.ArgumentParser(description="Check and manage import progress")
    parser.add_argument('action', choices=['status', 'logs', 'reset', 'pause', 'resume'], 
                       help='Action to perform')
    parser.add_argument('--lines', type=int, default=50, 
                       help='Number of log lines to show (default: 50)')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        show_status()
    elif args.action == 'logs':
        show_logs(args.lines)
    elif args.action == 'reset':
        confirm = input("Are you sure you want to reset progress? This will start import from the beginning. (y/N): ")
        if confirm.lower() == 'y':
            reset_progress()
        else:
            print("Reset cancelled.")
    elif args.action == 'pause':
        pause_import()
    elif args.action == 'resume':
        resume_import()

if __name__ == "__main__":
    import re
    main() 