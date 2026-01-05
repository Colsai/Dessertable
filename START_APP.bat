@echo off
REM Dessertable - Easy Startup Script for Windows
REM Double-click this file to launch the application

echo ========================================
echo Dessertable - Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please make sure Python is installed and in your PATH
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the GUI launcher
echo.
echo Starting Dessertable GUI Launcher...
echo.
python launcher.py

REM If launcher exits, deactivate venv
call venv\Scripts\deactivate.bat
