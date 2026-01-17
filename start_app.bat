@echo off
REM BSK Training Video Generator - Startup Script
REM This script helps diagnose and start the application

echo ==========================================
echo   BSK Training Video Generator
echo   Startup and Diagnostic Script
echo ==========================================
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)
py --version
echo.

REM Check if virtual environment should be used
if exist "venv\Scripts\activate.bat" (
    echo [2/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [2/4] No virtual environment found, using global Python
)
echo.

REM Run diagnostic test
echo [3/4] Running system diagnostic...
py debug_version_test.py
echo.

REM Start the application
echo [4/4] Starting Streamlit application...
echo.
echo The application will open in your default browser.
echo To stop the application, press Ctrl+C in this window.
echo.
echo ==========================================
echo   Starting BSK Training Video Generator
echo ==========================================
echo.

py -m streamlit run app.py

echo.
echo ==========================================
echo   Application Stopped
echo ==========================================
pause
