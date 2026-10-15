@echo off
title Installing Dependencies
cd /d "%~dp0"
echo ======================================================
echo Installing required libraries from requirements.txt...
echo ======================================================

python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================
    echo Installation completed successfully!
    echo You can now start the application using run.bat
    echo ======================================================
) else (
    echo.
    echo ======================================================
    echo An error occurred during installation.
    echo Please make sure Python is installed and added to PATH.
    echo ======================================================
)

pause
