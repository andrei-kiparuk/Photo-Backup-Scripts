SOURCE_FOLDER="/Users/akiparuk/Downloads/takeout"
UNPACK_FOLDER="/Volumes/RAID/unpack"
DONE_FOLDER="/Volumes/G-DRIVE/done"

# Create the "done" folder if it doesn't exist
mkdir -p "$DONE_FOLDER"

for file in "$SOURCE_FOLDER"/*.zip; do
  echo "Processing: $file"
  
  # Unzip the file
  unar -f -o "$UNPACK_FOLDER" "$file"
  
  # Remove unnecessary files
  find "$UNPACK_FOLDER" -type f \( \
    -iname "*.png" -o -iname "*.png.json" -o -iname "*.vob" -o -iname "*.vob.json" -o -iname "*.mkv" -o -iname "*.mkv.json" -o -iname "*.ts" -o -iname "*.ts.json" -o -iname "*.avi" -o -iname "*.avi.json" \
    -o -iname "GX*" -o -iname "GO*" -o -iname "GH*" -o -iname "*.3gp" -o -iname "*.3gp.json" -o -iname "*.webp" -o -iname "*.webp.json" -o -iname "*.mpg" -o -iname "*.mpg.json" \
    -o -iname "*.mpeg" -o -iname "*.mpeg.json" -o -iname "Свадьба Кати*" -o -iname "DSC*" \
  \) -delete -print
  
  # Move the processed archive to the "done" folder
  mv "$file" "$DONE_FOLDER"
  echo "Moved $file to $DONE_FOLDER"
done
