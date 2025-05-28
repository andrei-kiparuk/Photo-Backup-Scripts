#!/bin/bash

MAX_RETRIES=50
retry_count=0
last_imported=0

while [ $retry_count -lt $MAX_RETRIES ]; do
    osxphotos import /Volumes/T7/inprocess --parse-folder-date %Y/%m/%d$ --sidecar --exiftool --skip-dups --resume --walk --verbose --stop-on-error 5 2>&1 | tee -a import.log
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "Import completed successfully."
        break
    else
        current_imported=$(grep -c "Imported:" import.log)
        if [ $current_imported -gt $last_imported ]; then
            last_imported=$current_imported
            echo "Imported $current_imported files so far. Restarting Photos app..."
            # Force quit Photos if needed
            osascript -e 'tell application "System Events" to tell process "Photos" to keystroke return'
            osascript -e 'tell application "System Events" to tell process "Photos" to keystroke return'
            osascript -e 'tell application "System Events" to tell process "Photos" to keystroke return'
            osascript -e 'tell application "System Events" to tell process "Photos" to keystroke return'
            osascript -e 'tell application "System Events" to tell process "Photos" to keystroke return'
            osascript -e 'tell application "Photos" to quit'
            sleep 5
            if pgrep Photos > /dev/null; then
                echo "Photos is still running. Forcing quit..."
                killall -9 Photos
            fi
            echo "Photos has been quit. Proceeding..."
            sleep 10
            retry_count=$((retry_count + 1))
        else
            echo "No progress made. Stopping."
            break
        fi
    fi
done

if [ $retry_count -eq $MAX_RETRIES ]; then
    echo "Maximum retries reached. Import may not have completed."
else
    echo "Import finished after $retry_count retries."
fi