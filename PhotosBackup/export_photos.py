import os
import osxphotos
import datetime
from pathlib import Path

def create_folder_structure(date, base_path):
    """Create YYYY/MM/DD folder structure based on the photo's date."""
    year = date.year
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"
    folder_path = os.path.join(base_path, str(year), month, day)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def export_and_delete_photo(photo, export_path):
    """Export a single photo/video, preserve metadata, and delete from Photos library."""
    # Get the photo's date (use creation date or original date if available)
    photo_date = photo.date or datetime.datetime.now()
    
    # Create destination folder
    dest_folder = create_folder_structure(photo_date, export_path)
    
    # Export the photo/video, preserving original format and metadata
    exported_files = photo.export(
        dest=dest_folder,
        use_photos_export=True,  # Preserve metadata
        timeout=30
    )
    
    # Log exported files
    for file in exported_files:
        try:
            file_path = Path(file)
            if file_path.exists():
                print(f"Exported: {file_path}")
            else:
                print(f"File not found after export: {file_path}")
        except Exception as e:
            print(f"Error processing {file}: {e}")
    
    # Delete the photo from the Photos library
    try:
        photo.delete()
        print(f"Deleted from Photos library: {photo.original_filename}")
    except Exception as e:
        print(f"Error deleting {photo.original_filename} from Photos library: {e}")

def main():
    # Define export path (modify as needed)
    export_base_path = os.path.expanduser("/Volumes/G-DRIVE/iCloud")
    
    # Initialize Photos database
    photosdb = osxphotos.PhotosDB()
    
    # Get all photos and videos
    photos = photosdb.photos()
    
    print(f"Found {len(photos)} photos/videos to process.")
    
    # Process each photo/video one by one
    for idx, photo in enumerate(photos, 1):
        print(f"Processing {idx}/{len(photos)}: {photo.original_filename}")
        try:
            export_and_delete_photo(photo, export_base_path)
        except Exception as e:
            print(f"Error processing {photo.original_filename}: {e}")
    
    print("Export and deletion from Photos library complete.")

if __name__ == "__main__":
    main()