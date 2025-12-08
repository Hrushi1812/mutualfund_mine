@echo off
cd /d "%~dp0"
echo Activating venv...
call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Installation failed!
    pause
    exit /b 1
)
echo.
echo Installation complete.
pause
