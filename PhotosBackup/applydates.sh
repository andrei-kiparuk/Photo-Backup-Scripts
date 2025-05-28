#!/bin/bash

# Root directory
ROOT="/Volumes/G-DRIVE/processed"
count=0

echo "Starting processing under $ROOT..."
echo "-----------------------------------"

find "$ROOT" -type f | while read -r file; do
    # Extract directory components (YYYY/MM/DD)
    dd_dir="$(dirname "$file")"           # e.g. .../2018/08/22
    day="$(basename "$dd_dir")"           # 22
    mm_dir="$(dirname "$dd_dir")"         # .../2018/08
    month="$(basename "$mm_dir")"         # 08
    yyyy_dir="$(dirname "$mm_dir")"       # .../2018
    year="$(basename "$yyyy_dir")"        # 2018

    # Get the current modification time of the file
    # Format: YYYY-MM-DD HH:MM:SS
    original_mod_time_str=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$file")
    if [ -z "$original_mod_time_str" ]; then
        echo "Skipping $file - cannot read modification time."
        continue
    fi

    # Parse the original modification time
    orig_year=$(echo "$original_mod_time_str" | cut -d'-' -f1)
    orig_month=$(echo "$original_mod_time_str" | cut -d'-' -f2)
    orig_day_time=$(echo "$original_mod_time_str" | cut -d'-' -f3)
    orig_day=$(echo "$orig_day_time" | cut -d' ' -f1)
    orig_time=$(echo "$orig_day_time" | cut -d' ' -f2) # HH:MM:SS

    # Compare original date vs new desired date
    original_date="${orig_year}-${orig_month}-${orig_day}"
    new_date="${year}-${month}-${day}"

    # If the date is already correct, skip
    if [ "$original_date" = "$new_date" ]; then
        echo "Skipping $file - already has correct date ($original_date)."
        continue
    fi

    echo "Processing file: $file"
    echo "  Current date: $original_date $orig_time"
    echo "  New date:     $new_date (keeping time: $orig_time)"

    # Convert HH:MM:SS into HHMMSS parts for touch
    HH=$(echo "$orig_time" | cut -d':' -f1)
    MM=$(echo "$orig_time" | cut -d':' -f2)
    SS=$(echo "$orig_time" | cut -d':' -f3)

    # Construct 'touch' friendly date: [[CC]YY]MMDDhhmm[.SS]
    # e.g. year=2018, month=08, day=22, HH=12, MM=34, SS=56 -> 201808221234.56
    touch_time="${year}${month}${day}${HH}${MM}.${SS}"

    # Apply modification time (which also sets access time)
    if ! touch -t "$touch_time" "$file"; then
        echo "  [ERROR] Failed to update modification time with touch."
        continue
    fi

    # SetFile date format: MM/DD/YYYY HH:MM:SS
    setfile_date="${month}/${day}/${year} ${orig_time}"
    if ! SetFile -d "$setfile_date" "$file"; then
        echo "  [ERROR] Failed to update creation time with SetFile."
        continue
    fi

    echo "  Updated successfully."
    echo

    count=$((count + 1))
done

echo "-----------------------------------"
echo "Processing complete. Total files updated: $count"
