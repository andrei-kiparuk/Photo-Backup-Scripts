-- Declare globals so they’re accessible inside handlers
global baseExportDir, logFile

-- Set base export directory (fixed path)
set baseExportDir to "/Volumes/G-DRIVE/iCloudExport"
set logFile to baseExportDir & "/export_log.txt"

-- Handler to log messages to both the log file and console output
on logMessage(theMessage)
    global logFile
    do shell script "echo " & quoted form of (theMessage & return) & " >> " & quoted form of logFile
    log theMessage
end logMessage

logMessage("=== Starting export process at " & (current date as string) & " ===")

tell application "Photos"
    -- Get every media item (photos and videos)
    set photoList to every media item
    set totalCount to count of photoList
    logMessage("Total items to process: " & totalCount as string)
    
    repeat with aPhoto in photoList
        try
            -- Get the creation date
            set photoDate to date of aPhoto
            set y to year of photoDate as string
            
            -- Format month with two digits
            set m to month of photoDate as integer
            if m < 10 then
                set mStr to "0" & m as string
            else
                set mStr to m as string
            end if
            
            -- Format day with two digits
            set d to day of photoDate as integer
            if d < 10 then
                set dStr to "0" & d as string
            else
                set dStr to d as string
            end if
            
            -- Attempt to get a location name; if none, use "NoLocation"
            try
                set locObj to location of aPhoto
                if locObj is not missing value then
                    set locName to name of locObj
                    if (locName is missing value) or (locName = "") then set locName to "NoLocation"
                else
                    set locName to "NoLocation"
                end if
            on error
                set locName to "NoLocation"
            end try
            
            -- Build subfolder structure: YYYY/MM/DD-location
            set subfolder to y & "/" & mStr & "/" & dStr & "-" & locName
            set exportPath to baseExportDir & "/" & subfolder
            
            logMessage("Processing item with date " & photoDate as string & " to export path: " & exportPath)
            
            -- Create the destination folder (and any needed parent folders)
            do shell script "mkdir -p " & quoted form of exportPath
            logMessage("Created folder (if not exists): " & exportPath)
            
            -- Retry logic for exporting the original file
            set maxAttempts to 3
            set attempt to 1
            set exportSuccess to false
            repeat while attempt ≤ maxAttempts and not exportSuccess
                try
                    export aPhoto to exportPath with original
                    set exportSuccess to true
                    logMessage("Successfully exported item to " & exportPath & " on attempt " & attempt)
                on error errMsg number errNum
                    if errNum = -1741 then
                        logMessage("Attempt " & attempt & ": error -1741 encountered (original not available locally). Waiting 5 seconds to retry.")
                        delay 5
                    else
                        logMessage("Attempt " & attempt & ": error exporting item: " & errMsg)
                        exit repeat
                    end if
                end try
                set attempt to attempt + 1
            end repeat
            
            if not exportSuccess then
                logMessage("Failed to export item after " & maxAttempts & " attempts. Moving to next item.")
            else
                -- Delete the item from the Photos library after successful export
                try
                    delete aPhoto
                    logMessage("Deleted item from Photos library.")
                on error errMsg number errNum
                    logMessage("Error deleting item (error " & errNum & "): " & errMsg)
                end try
            end if
            
        on error errOuter number errOuterNum
            logMessage("Unexpected error processing an item (error " & errOuterNum & "): " & errOuter)
        end try
    end repeat
end tell

logMessage("=== Export process finished at " & (current date as string) & " ===")