# PowerShell script to find GoPro files by filename patterns and move them to another drive while preserving folder structure

# Configuration
$sourceDrive = "E:\" # Source drive to search (e.g., "D:\")
$destinationDrive = "D:\avi_Backup" # Destination drive/path (e.g., "E:\GoPro_Backup")
$goproFileNamePatterns = @("*.avi*") # Filename patterns for GoPro files (e.g., GOPR1234.MP4, GH010123.MP4)

# Ensure destination drive exists
if (-not (Test-Path $destinationDrive)) {
    Write-Host "Destination path does not exist. Creating: $destinationDrive"
    New-Item -ItemType Directory -Path $destinationDrive -Force
}

# Function to move files while preserving folder structure
function Move-GoProFiles {
    param (
        [string]$SourcePath,
        [string]$DestinationPath
    )

    # Get all files matching GoPro filename patterns
    foreach ($pattern in $goproFileNamePatterns) {
        Get-ChildItem -Path $SourcePath -Recurse -Include $pattern -File | ForEach-Object {
            $file = $_
            # Calculate relative path
            $relativePath = $file.FullName.Substring($SourcePath.Length)
            $destFilePath = Join-Path $DestinationPath $relativePath

            # Ensure destination directory exists
            $destDir = Split-Path $destFilePath -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force
            }

            # Move file
            Write-Host "Moving: $($file.FullName) to $destFilePath"
            try {
                Move-Item -Path $file.FullName -Destination $destFilePath -Force -ErrorAction Stop
            } catch {
                Write-Host "Error moving $($file.FullName): $_" -ForegroundColor Red
            }
        }
    }
}

# Validate source drive
if (-not (Test-Path $sourceDrive)) {
    Write-Host "Source drive $sourceDrive does not exist. Exiting." -ForegroundColor Red
    exit
}

# Start moving files
Write-Host "Starting to search for GoPro files in $sourceDrive"
Move-GoProFiles -SourcePath $sourceDrive -DestinationPath $destinationDrive
Write-Host "File transfer completed."