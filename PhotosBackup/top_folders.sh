#!/usr/bin/env bash

# Path to your top-level directory (change as needed)
base_dir="/Volumes/G-DRIVE/processed"

# Navigate to the base directory
cd "$base_dir" || { echo "Failed to navigate to $base_dir"; exit 1; }

# Find all files, extract their YYYY/MM/DD parent directories, count the files per directory, 
# sort by count descending, and print the top 10.
find . -type f | \
    awk -F/ 'NF>=5 { print $2"/"$3"/"$4 }' | \
    sort | \
    uniq -c | \
    sort -nr | \
    head -10
