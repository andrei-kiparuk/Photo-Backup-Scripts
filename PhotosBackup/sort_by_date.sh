#!/usr/bin/env bash

set -euo pipefail

# Directories
input_directory="/Volumes/G-DRIVE/unpack/"
processed_directory="/Volumes/G-DRIVE/processed"

# Ensure unique filename by appending _1, _2, ...
ensure_unique_filename() {
    local output_path="$1"
    if [[ ! -e "$output_path" ]]; then
        echo "$output_path"
        return
    fi

    local base ext new_output_path counter
    base="$(echo "$output_path" | sed 's/\.[^.]*$//')"
    ext="${output_path#$base}"

    counter=1
    new_output_path="${base}_${counter}${ext}"

    while [[ -e "$new_output_path" ]]; do
        ((counter++))
        new_output_path="${base}_${counter}${ext}"
    done

    echo "$new_output_path"
}

# Extract possible dates from metadata using exiftool
extract_dates_from_metadata() {
    local file_path="$1"
    exiftool -s -s -s -CreateDate -DateTimeOriginal -MediaCreateDate -ContentCreateDate "$file_path" 2>/dev/null
}

# Extract date from path (YYYY/MM/DD)
extract_date_from_path() {
    local file_path="$1"
    local path_date
    path_date=$(echo "$file_path" | grep -Eo '[0-9]{4}/[0-9]{2}/[0-9]{2}' || true)
    echo "$path_date"
}

# Determine oldest date for a file
get_oldest_date() {
    local file_path="$1"
    local dates=()
    local meta_lines path_date fallback_date

    meta_lines=$(extract_dates_from_metadata "$file_path")
    while IFS= read -r line; do
        # line like "2020:05:03 12:34:56"
        if [[ "$line" =~ ^[0-9]{4}:[0-9]{2}:[0-9]{2} ]]; then
            local d=$(echo "$line" | awk '{print $1}' | sed 's/:/\//g')
            dates+=("$d")
        fi
    done < <(echo "$meta_lines")

    path_date=$(extract_date_from_path "$file_path")
    if [[ -n "$path_date" ]]; then
        dates+=("$path_date")
    fi

    if [[ ${#dates[@]} -eq 0 ]]; then
        # fallback to file modification date
        fallback_date=$(date -r "$file_path" +%Y/%m/%d)
        dates+=("$fallback_date")
    fi

    IFS=$'\n' sorted=($(sort <<<"${dates[*]}"))
    unset IFS
    oldest_date="${sorted[0]}"
    echo "$oldest_date"
}

# Move file to processed folder by date
move_to_processed() {
    local src="$1"
    local processed_root="$2"

    local date_folder
    date_folder=$(get_oldest_date "$src")
    local processed_folder="${processed_root}/${date_folder}"
    mkdir -p "$processed_folder"

    local filename
    filename=$(basename "$src")
    local dest="${processed_folder}/${filename}"
    dest=$(ensure_unique_filename "$dest")

    mv "$src" "$dest"
    echo "Moved: $src -> $dest"
}

process_files() {
    local input_dir="$1"
    local processed_dir="$2"

    find "$input_dir" -type f | while IFS= read -r file_path; do
        file=$(basename "$file_path")

        # Skip files starting with ._
        if [[ "$file" == ._* ]]; then
            echo "Skipping file: $file"
            continue
        fi

        if ! move_to_processed "$file_path" "$processed_dir"; then
            echo "Error moving file $file_path"
        fi
    done
}

process_files "$input_directory" "$processed_directory"
