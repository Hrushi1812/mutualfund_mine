@echo off
cd /d "%~dp0"

echo ==========================================
echo Starting Backend...
echo ==========================================

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found at venv\Scripts\activate.bat
    echo Please create it: python -m venv venv
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Checking python version...
python --version
echo.

echo Starting Uvicorn server...
python -m uvicorn app:app --reload

if %errorlevel% neq 0 (
    echo.
    echo Server stopped with error.
)

pause
