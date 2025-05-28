--------------------------------------------------------------------------------
-- CONFIGURATION
--------------------------------------------------------------------------------
set sourceFolder to "/Volumes/SlowDisk/iCloudBackup"
set destinationFolder to "/Volumes/SlowDisk/Done"
-- Folder for files that fail twice
set failedFolder to "/Volumes/SlowDisk/Failed"

--------------------------------------------------------------------------------
-- Convert source folder to a POSIX path (no trailing slash needed)
--------------------------------------------------------------------------------
set sourceFolderPosix to POSIX path of sourceFolder

--------------------------------------------------------------------------------
-- 1) Find all files in the source folder, excluding .DS_Store
--------------------------------------------------------------------------------
set folderList to do shell script "find " & quoted form of sourceFolderPosix & " -type f -not -name '.DS_Store' | sort"
set folderLines to paragraphs of folderList

--------------------------------------------------------------------------------
-- 2) Handler to import a single file
--------------------------------------------------------------------------------
on importFile(folderPath)
    (*
      Returns 'true' if successful,
      or throws an error if Photos fails or returns no items.
    *)
    tell application "Photos"
        set fileAlias to (POSIX file folderPath) as alias
        
        set importedItems to import fileAlias skip check duplicates true
        
        if (count of importedItems) = 0 then
            error "Photos did not import the file: " & folderPath
        end if
    end tell
    return true
end importFile

--------------------------------------------------------------------------------
-- 3) Helper handler to force-quit Photos
--------------------------------------------------------------------------------
on forceQuitPhotos()
    -- Attempt a normal quit
    tell application "Photos"
        try
            quit
        end try
    end tell
    
    -- Wait a moment for normal quit
    delay 2
    
    -- If still running, kill it. 
    -- The ‘|| true’ part ensures we don’t throw an error if Photos isn’t running.
    try
        do shell script "killall 'Photos' || true"
    end try
end forceQuitPhotos

--------------------------------------------------------------------------------
-- 4) Main logic: import each file, retry once on error.
--    If second attempt fails, move file to 'failedFolder' and continue.
--------------------------------------------------------------------------------
tell application "Photos"
    try
        repeat with folderPath in folderLines
            set folderPath to (folderPath as text)
            
            --------------------------------------------------------------------------------
            -- FIRST ATTEMPT
            --------------------------------------------------------------------------------
            try
                log ("[1st attempt] Importing: " & folderPath)
                my importFile(folderPath)
                
                --------------------------------------------------------------------------------
                -- MOVE FILE TO DESTINATION FOLDER AFTER SUCCESSFUL IMPORT
                --------------------------------------------------------------------------------
                set relativePath to text ((length of sourceFolderPosix) + 1) thru -1 of folderPath
                set destinationPath to destinationFolder & "/" & relativePath
                
                -- Create any necessary subfolders in the destination
                do shell script "mkdir -p " & quoted form of (do shell script "dirname " & quoted form of destinationPath)
                
                -- Move the file to the destination folder
                do shell script "mv " & quoted form of folderPath & " " & quoted form of destinationPath
                log ("Successfully imported and moved " & folderPath & " to " & destinationPath)
                
            on error firstErrMsg number firstErrNum
                log ("[1st attempt] Error importing " & folderPath & ": " & firstErrMsg & " (Error " & firstErrNum & ")")
                
                --------------------------------------------------------------------------------
                -- FORCE-QUIT PHOTOS, WAIT, THEN REOPEN
                --------------------------------------------------------------------------------
                my forceQuitPhotos()
                delay 2
                tell application "Photos" to activate
                delay 2
                --------------------------------------------------------------------------------
                -- SECOND ATTEMPT
                --------------------------------------------------------------------------------
                try
                    log ("[2nd attempt] Importing: " & folderPath)
                    my importFile(folderPath)
                    
                    --------------------------------------------------------------------------------
                    -- MOVE FILE TO DESTINATION FOLDER AFTER SUCCESSFUL IMPORT (2nd attempt)
                    --------------------------------------------------------------------------------
                    set relativePath to text ((length of sourceFolderPosix) + 1) thru -1 of folderPath
                    set destinationPath to destinationFolder & "/" & relativePath
                    
                    do shell script "mkdir -p " & quoted form of (do shell script "dirname " & quoted form of destinationPath)
                    do shell script "mv " & quoted form of folderPath & " " & quoted form of destinationPath
                    log ("Successfully imported and moved " & folderPath & " to " & destinationPath & " after retry.")
                    
                on error secondErrMsg number secondErrNum
                    --------------------------------------------------------------------------------
                    -- If second attempt fails: LOG, MOVE to 'failedFolder', and CONTINUE
                    --------------------------------------------------------------------------------
                    log ("[2nd attempt] Error importing " & folderPath & ": " & secondErrMsg & " (Error " & secondErrNum & ")")
                    
                    -- 1) Remove the sourceFolderPosix prefix to build relativePath
                    set relativePath to text ((length of sourceFolderPosix) + 1) thru -1 of folderPath
                    
                    -- 2) Build the new full path in the failed folder
                    set destinationPath to failedFolder & "/" & relativePath
                    
                    -- 3) Make any necessary subdirectories under 'failedFolder'
                    do shell script "mkdir -p " & quoted form of (do shell script "dirname " & quoted form of destinationPath)
                    
                    -- 4) Move the file into 'failedFolder'
                    do shell script "mv " & quoted form of folderPath & " " & quoted form of destinationPath
                    log ("File moved to " & destinationPath & " due to failed import.")
                    
                    my forceQuitPhotos()
                    delay 2
                    --------------------------------------------------------------------------------
                    -- Check free space in home folder
                    --------------------------------------------------------------------------------
                    set freeKB to do shell script "df -k ~ | tail -1 | awk '{print $4}'"
                    set freeSpaceGB to (freeKB as integer) / 1048576

                    if freeSpaceGB < 100 then
                        log ("[ERROR] Less than 100GB of free space at home directory (~). Stopping script.")
                        error "Insufficient free space in home directory."
                    end if



                    -- Continue to next file



                end try
            end try
        end repeat
        
    on error finalErrMsg number finalErrNum
        log ("[FATAL] Script stopped due to error: " & finalErrMsg & " (Error " & finalErrNum & ")")
        error finalErrMsg number finalErrNum
    end try
end tell
