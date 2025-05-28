on run argv
    set filePath to item 1 of argv
    set sourceFolder to "/Volumes/G-DRIVE/Converted"
    set destinationFolder to "/Volumes/G-DRIVE/Imported"
    set failedFolder to "/Volumes/G-DRIVE/Failed"
    
    -- Calculate relative path
    set sourceFolderPosix to POSIX path of sourceFolder
    set filePathPosix to filePath
    set relativePath to text ((length of sourceFolderPosix) + 1) thru -1 of filePathPosix
    
    try
        -- First attempt
        my importFile(filePath)
        -- Move to destination
        set destinationPath to destinationFolder & "/" & relativePath
        do shell script "mkdir -p " & quoted form of (do shell script "dirname " & quoted form of destinationPath)
        do shell script "mv " & quoted form of filePath & " " & quoted form of destinationPath
        log ("Imported and moved to " & destinationPath)
    on error errMsg number errNum
        log ("[1st attempt] Error: " & errMsg & " (" & errNum & ")")
        -- Force quit Photos, wait, reopen
        my forceQuitPhotos()
        delay 2
        -- tell application "Photos" to activate
        delay 2
        try
            -- Second attempt
            my importFile(filePath)
            -- Move to destination
            set destinationPath to destinationFolder & "/" & relativePath
            do shell script "mkdir -p " & quoted form of (do shell script "dirname " & quoted form of destinationPath)
            do shell script "mv " & quoted form of filePath & " " & quoted form of destinationPath
            log ("Imported and moved to " & destinationPath & " after retry")
        on error
            -- Move to failed
            my forceQuitPhotos()
            delay 2
            set failedPath to failedFolder & "/" & relativePath
            do shell script "mkdir -p " & quoted form of (do shell script "dirname " & quoted form of failedPath)
            do shell script "mv " & quoted form of filePath & " " & quoted form of failedPath
            log ("Moved to " & failedPath & " due to repeated failure")
        end try
    end try
end run

on importFile(folderPath)
    tell application "Photos"
        set fileAlias to (POSIX file folderPath) as alias
        set importedItems to import fileAlias skip check duplicates true
        if (count of importedItems) = 0 then
            error "Photos did not import the file: " & folderPath
        end if
    end tell
end importFile

on forceQuitPhotos()
    tell application "Photos"
        try
            quit
        end try
    end tell
    delay 2
    try
        do shell script "killall 'Photos' || true"
    end try
end forceQuitPhotos