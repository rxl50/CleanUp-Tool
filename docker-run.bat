@echo off
REM Convenience script to run CleanUp Tool in Docker (Windows)

echo CleanUp Tool - Docker Runner
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Build image if it doesn't exist
docker images | findstr cleanup-tool >nul 2>&1
if errorlevel 1 (
    echo Building Docker image...
    docker build -t cleanup-tool .
    echo.
)

echo.
echo WARNING: Docker GUI support on Windows is limited.
echo For best results, run natively with: python main.py
echo.
echo Running with VNC (connect to localhost:5900 with VNC viewer)...
echo.

docker run -it --rm ^
    -p 5900:5900 ^
    -v "%CD%\backups:/app/backups" ^
    -v "%CD%\logs:/app/logs" ^
    -v "%CD%\config:/app/config" ^
    cleanup-tool

pause

