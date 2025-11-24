@echo off
REM Build script for creating standalone executable (Windows)

echo ========================================
echo CleanUp Tool - Standalone Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo Step 1: Installing build dependencies...
pip install -r build_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install build dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Installing application dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install application dependencies
    pause
    exit /b 1
)
echo.

echo Step 3: Building standalone executable...
echo This may take a few minutes...
echo.
python build_standalone.py
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Your standalone executable is in the 'dist' folder:
echo   dist\CleanUpTool.exe
echo.
echo You can now distribute this .exe file to other Windows computers
echo without requiring Python to be installed.
echo.
pause

