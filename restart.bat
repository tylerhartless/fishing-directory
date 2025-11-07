@echo off
REM Restart Docker Compose services in the correct order
REM This ensures the API is fully healthy before the frontend starts

echo Stopping containers...
docker compose down

echo.
echo Starting containers with dependency order...
docker compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 3 /nobreak >nul

echo.
echo === API Container Status ===
docker logs fishing_directory_api --tail 5

echo.
echo === Frontend Container Status ===
docker logs fishing_directory_frontend --tail 5

echo.
echo Services are starting up!
echo Frontend: http://localhost:4321
echo API: http://localhost:8000
echo.
echo To follow logs:
echo   docker compose logs -f
