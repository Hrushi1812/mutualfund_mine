@echo off
echo 🚀 Starting build process...

REM Install backend dependencies
echo 📦 Installing backend dependencies...
pip install -r backend/requirements.txt

REM Navigate to frontend directory
echo 📁 Navigating to frontend directory...
cd frontend

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
npm install

REM Check if node_modules exists
if not exist "node_modules" (
    echo ❌ Frontend dependencies installation failed
    pause
    exit /b 1
)

REM Build frontend
echo 🔨 Building frontend...
npm run build

REM Check if build was successful
if not exist "dist" (
    echo ❌ Frontend build failed - dist directory not found
    echo 📋 Checking for build errors...
    dir
    pause
    exit /b 1
)

echo ✅ Frontend build successful

REM Create backend static directory
echo 📁 Creating backend static directory...
mkdir ..\backend\static 2>nul

REM Copy built files
echo 📋 Copying built files...
xcopy /E /I dist ..\backend\static\

REM Verify files were copied
if exist "..\backend\static\index.html" (
    echo ✅ Files copied successfully
    echo 📋 Static files:
    dir ..\backend\static
) else (
    echo ❌ Failed to copy files
    pause
    exit /b 1
)

echo 🎉 Build completed successfully!
pause
