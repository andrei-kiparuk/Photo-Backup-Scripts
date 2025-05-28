#!/bin/bash

# Exit on any error
set -e

# Step 1: Disconnect Google Drive account (requires manual interaction)
echo "Please disconnect your Google Drive account manually:"
echo "1. Click the Google Drive icon in the menu bar."
echo "2. Go to Settings > Preferences > Settings > Disconnect Account."
echo "3. Confirm disconnection."
read -p "Press Enter after disconnecting the account..."

# Step 2: Quit Google Drive
echo "Quitting Google Drive..."
pkill -f "Google Drive" || echo "Google Drive was not running."

# Step 3: Remove Google Drive application
echo "Removing Google Drive application..."
if [ -d "/Applications/Google Drive.app" ]; then
    sudo rm -rf "/Applications/Google Drive.app"
else
    echo "Google Drive.app not found in /Applications."
fi

# Step 4: Remove Google Drive-related files from Library
echo "Removing Google Drive residual files..."
declare -a paths=(
    "~/Library/Application Support/Google/Drive"
    "~/Library/Caches/com.google.GoogleDrive"
    "~/Library/Preferences/com.google.GoogleDrive.plist"
    "~/Library/Containers/com.google.GoogleDrive"
    "~/Library/Group Containers/google.drive"
    "~/Library/Application Scripts/com.google.GoogleDrive"
    "~/Library/Cookies/com.google.GoogleDrive.binarycookies"
)

for path in "${paths[@]}"; do
    if [ -e "$path" ]; then
        sudo rm -rf "$path"
        echo "Removed: $path"
    else
        echo "Not found: $path"
    fi
done

# Step 5: Remove Google Drive folder from CloudStorage (if exists)
echo "Removing Google Drive folder from CloudStorage..."
if [ -d "~/Library/CloudStorage/GoogleDrive*" ]; then
    sudo rm -rf ~/Library/CloudStorage/GoogleDrive*
    echo "Removed Google Drive folder from CloudStorage."
else
    echo "Google Drive folder not found in CloudStorage."
fi

# Step 6: Empty the Trash
echo "Emptying the Trash..."
osascript -e 'tell app "Finder" to empty trash'

echo "Google Drive has been completely uninstalled."