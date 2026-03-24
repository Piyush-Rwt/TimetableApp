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
powershell -Command "Compress-Archive -Path 'dist\ScheduleForge\*' -DestinationPath 'ScheduleForge_v1.0.zip' -Force"

echo Build complete!
pause
