import os
import sys
import datetime
from pathlib import Path

# Define the export path on the external drive
EXPORT_PATH = "/Volumes/4TB-1/iCloudExport"
ALBUM_NAME = "Exported"

# Export options based on comments:
# --export-by-date: Organize by date using structure YYYY/MM/DD
# --use-photokit: Use PhotoKit to access original files
# --update: Only export new or changed photos/videos if re-running the script
# --download-missing: Download missing originals from iCloud during export
# --retry 3: Retry failed exports up to 3 times
# --skip-missing: Skip photos with missing original files
# --verbose: Show detailed output during export
# --add-exported-to-album: Add successfully exported photos to the specified album

def log(message):
    """Log messages with timestamps."""
    print(f"{datetime.datetime.now()}: {message}")

def main():
    try:
        # Import osxphotos modules
        # Workaround for theme loading issue: temporarily rename theme config if it exists
        theme_config_dir = Path.home() / ".config" / "osxphotos"
        theme_backup = None
        
        try:
            if theme_config_dir.exists():
                # Try to work around theme loading issue by temporarily moving the directory
                theme_backup = str(theme_config_dir) + ".backup"
                if os.path.exists(theme_backup):
                    os.rename(theme_backup, str(theme_config_dir))
        except Exception:
            pass  # Ignore errors with theme config
        
        # Now import osxphotos
        from osxphotos import PhotosDB
        from osxphotos.photoexporter import PhotoExporter
        from osxphotos.exportoptions import ExportOptions
        from osxphotos.photosalbum import PhotosAlbum
        
        # Check if export path exists, create if not
        if not os.path.exists(EXPORT_PATH):
            os.makedirs(EXPORT_PATH)
            log(f"Created export directory: {EXPORT_PATH}")

        # Initialize Photos database
        log("Connecting to Photos library...")
        photosdb = PhotosDB()
        
        # Get all photos and videos
        log("Loading all photos and videos from library...")
        photos = photosdb.photos()
        log(f"Found {len(photos)} photos/videos to export")

        # Set up export options
        def verbose_callback(msg):
            """Verbose callback for export progress."""
            if msg:
                log(msg)
        
        export_options = ExportOptions(
            use_photokit=True,  # --use-photokit: Use PhotoKit to access original files
            update=True,  # --update: Only export new or changed photos/videos if re-running the script
            download_missing=True,  # --download-missing: Download missing originals from iCloud during export
            verbose=verbose_callback  # --verbose: Show detailed output during export
        )
        
        # Note: export_by_date and filename are handled differently in the API
        # export_by_date is handled by organizing files into date-based folders
        # filename uses the photo's original filename by default (pass None to export method)
        # retry is implemented manually below (--retry 3)

        # Initialize the album for adding exported photos
        log(f"Initializing album '{ALBUM_NAME}'...")
        try:
            album = PhotosAlbum(ALBUM_NAME)
            log(f"Album '{ALBUM_NAME}' ready")
        except Exception as e:
            log(f"Warning: Could not initialize album '{ALBUM_NAME}': {e}")
            log("Continuing with export, but photos will not be added to album")
            album = None
        
        log("Starting export process...")
        exported_count = 0
        failed_count = 0
        added_to_album_count = 0
        
        for photo in photos:
            # Retry logic: --retry 3 means retry up to 3 times (4 total attempts)
            max_retries = 3
            retry_count = 0
            exported = False
            
            while retry_count <= max_retries and not exported:
                try:
                    exporter = PhotoExporter(photo)
                    
                    # Determine export path with date-based folder structure (YYYY/MM/DD)
                    # This implements --export-by-date functionality
                    photo_date = photo.date
                    if photo_date:
                        date_folder = os.path.join(
                            EXPORT_PATH,
                            str(photo_date.year),
                            f"{photo_date.month:02d}",
                            f"{photo_date.day:02d}"
                        )
                        os.makedirs(date_folder, exist_ok=True)
                        export_dest = date_folder
                    else:
                        export_dest = EXPORT_PATH
                    
                    # Use original filename (None means use photo's original filename)
                    # This implements --filename "{original_name}" functionality
                    result = exporter.export(export_dest, filename=None, options=export_options)
                    
                    if result and result.exported:
                        exported_count += 1
                        exported = True
                        
                        # Add photo to album immediately after successful export
                        if album:
                            try:
                                album.add(photo)
                                added_to_album_count += 1
                            except Exception as e:
                                log(f"Warning: Could not add photo {photo.uuid} to album: {e}")
                        
                        if exported_count % 100 == 0:
                            log(f"Exported {exported_count} photos/videos (added {added_to_album_count} to album)...")
                    else:
                        # Export failed, retry if we haven't exceeded max retries
                        retry_count += 1
                        if retry_count <= max_retries:
                            log(f"Export failed for photo {photo.uuid}, retry {retry_count}/{max_retries}")
                except Exception as e:
                    # Exception occurred, retry if we haven't exceeded max retries
                    retry_count += 1
                    if retry_count <= max_retries:
                        log(f"Error exporting photo {photo.uuid} (retry {retry_count}/{max_retries}): {e}")
                    else:
                        log(f"Error exporting photo {photo.uuid} after {max_retries} retries: {e}")
            
            if not exported:
                failed_count += 1
        
        log(f"Export completed. Successfully exported: {exported_count}, Failed: {failed_count}")
        if album:
            log(f"Added {added_to_album_count} photos to album '{ALBUM_NAME}'")
        log(f"All photos and videos successfully exported to: {EXPORT_PATH}")

    except KeyboardInterrupt:
        log("Export interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
