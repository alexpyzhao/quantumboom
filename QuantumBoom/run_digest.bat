@echo off
REM QuantumBoom - Windows Batch Runner
REM This script runs QuantumBoom and handles basic error checking

echo.
echo ========================================
echo      QuantumBoom - Daily Run
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found
    echo Please run setup.py first or copy .env.template to .env
    pause
    exit /b 1
)

REM Run the digest
echo Running QuantumBoom...
echo.
python quantumboom.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ERROR: Digest failed to run successfully
    echo Check quantumboom.log for details
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: Digest completed successfully
    echo Check your email for the digest
)

REM Keep window open if run manually
if "%1"=="" pause

exit /b 0
