@echo off
REM Windows batch script to run the time-decay scoring script
REM Can be scheduled via Windows Task Scheduler

cd /d %~dp0

REM Ensure script is in container (copy if needed)
docker exec fishing_directory_api test -f /var/www/html/scripts/decay-scores.php || docker cp decay-scores.php fishing_directory_api:/var/www/html/scripts/decay-scores.php

REM Run the PHP script via Docker
docker exec fishing_directory_api php /var/www/html/scripts/decay-scores.php >> decay-scores.log 2>&1

REM Log completion
echo [%date% %time%] Decay script completed >> decay-scores.log

