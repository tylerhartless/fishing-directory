# PowerShell script to run the time-decay scoring script
# Can be scheduled via Windows Task Scheduler

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$decayScript = Join-Path $scriptDir "decay-scores.php"

# Change to script directory
Set-Location $scriptDir

# Run the PHP script via Docker
docker exec fishing_directory_api php /var/www/html/scripts/decay-scores.php

# Log the output
$logFile = Join-Path $scriptDir "decay-scores.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logFile -Value "[$timestamp] Decay script completed"

