@echo off
echo 🚀 Starting production build...

REM Install backend dependencies
echo 📦 Installing backend dependencies...
pip install -r backend/requirements.txt

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install

REM Show versions for debugging
echo 🔍 Environment info:
node --version
npm --version
echo Current directory: %CD%

REM Build frontend
echo 🔨 Building frontend...
npm run build

REM Verify build
echo ✅ Verifying build...
if not exist "dist" (
    echo ❌ Build failed - dist directory not found
    pause
    exit /b 1
)

echo 📁 Build contents:
dir dist

REM Create backend static directory
echo 📁 Creating backend static directory...
mkdir ..\backend\static 2>nul

REM Copy files
echo 📋 Copying files...
xcopy /E /I dist ..\backend\static\

REM Verify copy
echo ✅ Verifying copy...
if not exist "..\backend\static\index.html" (
    echo ❌ Copy failed - index.html not found
    pause
    exit /b 1
)

echo 📁 Static directory contents:
dir ..\backend\static

echo 🎉 Build completed successfully!
pause
