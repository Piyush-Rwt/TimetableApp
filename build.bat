@REM Build Script - build.bat
@REM Builds the ScheduleForge application into a standalone executable using PyInstaller.
@REM 
@REM What it does:
@REM 1. Cleans previous build artifacts (dist/, build/ directories)
@REM 2. Runs PyInstaller to package Python code and dependencies into executable
@REM 3. Copies additional files (scheduler.py, exam_db.py, version.json) to build output
@REM 4. Creates a zip archive in the releases/ folder for distribution
@REM
@REM Requirements:
@REM - Python with PyInstaller installed: pip install pyinstaller
@REM - All dependencies from requirements.txt installed
@REM
@REM Output:
@REM - dist/ScheduleForge/ - Standalone application folder
@REM - releases/ScheduleForge_v1.0.zip - Distributable zip file
@REM
@REM Usage:
@REM - Double-click this file or run: build.bat
@REM - The executable will be in dist/ScheduleForge/ScheduleForge.exe

@echo off
echo Starting build process for ScheduleForge...

:: Clean previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

:: Run PyInstaller
:: --onedir creates a folder dist/ScheduleForge/
:: --windowed prevents a console window from appearing
:: --add-data includes project folders
:: --hidden-import ensures specific modules are included
pyinstaller --noconfirm --onedir --windowed --name "ScheduleForge" ^
    --add-data "ui;ui" ^
    --add-data "db;db" ^
    --add-data "engine;engine" ^
    --add-data "saved_tt;saved_tt" ^
    --hidden-import "openpyxl" ^
    --hidden-import "requests" ^
    --hidden-import "PySide6" ^
    main.py

:: Copy additional files into the build directory
echo Copying extra files...
copy scheduler.py dist\ScheduleForge\
copy exam_db.py dist\ScheduleForge\
copy version.json dist\ScheduleForge\

:: Create Zip archive using PowerShell
echo Creating zip archive...
if not exist releases mkdir releases
powershell -Command "Compress-Archive -Path 'dist\ScheduleForge\*' -DestinationPath 'releases\ScheduleForge_v1.0.zip' -Force"

echo Build complete!
pause
