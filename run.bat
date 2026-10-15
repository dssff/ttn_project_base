@echo off
title Data and API Server
cd /d "%~dp0"
echo ======================================================
echo Starting Database and REST API Server...
echo Web UI:   http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo ======================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application stopped with an error.
)
pause
