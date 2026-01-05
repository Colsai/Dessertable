@echo off
REM Restaurant Finder - Troubleshooting Script
REM Run this to diagnose issues with the app

echo ========================================
echo Restaurant Finder - Troubleshooting
echo ========================================
echo.

REM Check Python
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo         Download from: https://python.org
    pause
    exit /b 1
) else (
    python --version
    echo [OK] Python is installed
)
echo.

REM Check virtual environment
echo [2/7] Checking virtual environment...
if exist "venv\" (
    echo [OK] Virtual environment exists
) else (
    echo [ERROR] Virtual environment not found
    echo [FIX] Run: python -m venv venv
    pause
    exit /b 1
)
echo.

REM Check dependencies
echo [3/7] Checking dependencies...
venv\Scripts\pip show Flask >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Dependencies not installed
    echo [FIX] Run: venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
) else (
    echo [OK] Dependencies installed
)
echo.

REM Check API key
echo [4/7] Checking API key configuration...
if exist ".env" (
    echo [OK] .env file exists
    findstr /C:"GOOGLE_PLACES_API_KEY=" .env >nul 2>&1
    if errorlevel 1 (
        echo [WARN] API key not found in .env
        echo [FIX] Edit .env and add: GOOGLE_PLACES_API_KEY=your_key_here
    ) else (
        findstr /C:"GOOGLE_PLACES_API_KEY=your_api_key_here" .env >nul 2>&1
        if errorlevel 1 (
            echo [OK] API key appears to be configured
        ) else (
            echo [WARN] API key is still set to placeholder value
            echo [FIX] Edit .env and replace with your actual API key
        )
    )
) else (
    echo [ERROR] .env file not found
    echo [FIX] Copy .env.example to .env and add your API key
    pause
    exit /b 1
)
echo.

REM Run comprehensive tests
echo [5/7] Running comprehensive tests...
venv\Scripts\python test_complete.py
if errorlevel 1 (
    echo [ERROR] Tests failed. See errors above.
    pause
    exit /b 1
)
echo.

REM Check port availability
echo [6/7] Checking if port 5000 is available...
netstat -ano | findstr ":5000" >nul 2>&1
if errorlevel 1 (
    echo [OK] Port 5000 is available
) else (
    echo [WARN] Port 5000 is already in use
    echo [INFO] The app may already be running, or another app is using this port
)
echo.

REM Try starting the app briefly
echo [7/7] Testing app startup...
echo [INFO] Starting app for 3 seconds...
timeout /t 3 /nobreak >nul 2>&1 & venv\Scripts\python run.py >nul 2>&1 &
timeout /t 3 /nobreak >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo [OK] App startup test complete
echo.

echo ========================================
echo Troubleshooting Complete!
echo ========================================
echo.
echo If all checks passed, the app should work.
echo.
echo To start the app:
echo   1. Double-click START_APP.bat
echo   2. Click "Start Server"
echo   3. Browser will open automatically
echo.
echo If you're still having issues:
echo   1. Check the error message carefully
echo   2. See USER_GUIDE.md Troubleshooting section
echo   3. Make sure your API key is correct
echo   4. Check you have internet connection
echo.
pause
