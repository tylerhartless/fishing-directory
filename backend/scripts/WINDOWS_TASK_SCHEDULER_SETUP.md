# Windows Task Scheduler Setup for Time-Decay Script

Since you're on Windows, use Windows Task Scheduler instead of cron to run the decay script daily.

## Quick Setup

### Option 1: Using the Batch Script (Recommended)

1. **Open Task Scheduler:**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create Basic Task:**
   - Click "Create Basic Task" in the right panel
   - Name: `Fishing Directory - Decay Scores`
   - Description: `Runs daily time-decay for species prevalence scores`

3. **Set Trigger:**
   - Trigger: Daily
   - Start time: 2:00 AM (or your preferred time)
   - Recur every: 1 days

4. **Set Action:**
   - Action: Start a program
   - Program/script: `C:\Users\tyash\Desktop\fishing-directory\backend\scripts\run-decay.bat`
   - Start in: `C:\Users\tyash\Desktop\fishing-directory\backend\scripts`

5. **Finish:**
   - Check "Open the Properties dialog for this task when I click Finish"
   - In Properties:
     - General tab: Check "Run whether user is logged on or not"
     - Conditions tab: Uncheck "Start the task only if the computer is on AC power" (if you want it to run on battery)
     - Settings tab: Check "Run task as soon as possible after a scheduled start is missed"

### Option 2: Using PowerShell Script

Same steps as above, but use:
- Program/script: `powershell.exe`
- Add arguments: `-File "C:\Users\tyash\Desktop\fishing-directory\backend\scripts\run-decay.ps1"`

## Verify Setup

1. **Test the script manually:**
   ```cmd
   cd C:\Users\tyash\Desktop\fishing-directory\backend\scripts
   run-decay.bat
   ```

2. **Check the log file:**
   - Open `decay-scores.log` in the scripts directory
   - Should see output from the decay script

3. **Test the scheduled task:**
   - Right-click the task in Task Scheduler
   - Select "Run"
   - Check the log file to verify it executed

## Troubleshooting

- **Docker not found:** Make sure Docker Desktop is running and the container `fishing_directory_api` exists
- **Script not found in container:** The batch script will auto-copy it if missing
- **Permission errors:** Run Task Scheduler as Administrator or ensure the task runs with appropriate permissions

## Manual Run (for testing)

You can always run the script manually:
```cmd
cd C:\Users\tyash\Desktop\fishing-directory\backend\scripts
docker exec fishing_directory_api php /var/www/html/scripts/decay-scores.php
```

