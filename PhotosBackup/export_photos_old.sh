#!/bin/bash

# Define the export path
EXPORT_PATH="/Users/akiparuk/Downloads/iCloud"

# Create the export directory if it doesn't exist
mkdir -p "$EXPORT_PATH"

# Export photos and videos using osxphotos, including live photo videos
osxphotos export "$EXPORT_PATH" \
    --exiftool \
    --exiftool-option "-m" \
    --use-photos-export \
    --use-photokit \
    --download-missing \
    --touch-file \
    --verbose \
    --update \
    --export-by-date \
    --sidecar json \
    --sidecar xmp \
    --retry 5