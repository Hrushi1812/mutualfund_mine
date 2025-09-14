@echo off
echo 🚀 Preparing Mutual Fund Tracker for Render deployment...

REM Check if we're in the right directory
if not exist "backend\requirements.txt" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo ✅ Project structure verified

REM Create production environment file
echo 📝 Creating production environment template...
(
echo # Production Environment Variables for Render
echo MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/mutual_fund_tracker
echo JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
echo ENVIRONMENT=production
echo DEBUG=false
echo CORS_ORIGINS=https://mutual-fund-tracker-frontend.onrender.com
) > backend\.env.production

echo ✅ Production environment file created

REM Check if all required files exist
echo 🔍 Checking deployment files...

if exist "render.yaml" (
    echo ✅ render.yaml exists
) else (
    echo ❌ render.yaml is missing
)

if exist "backend\Dockerfile" (
    echo ✅ backend\Dockerfile exists
) else (
    echo ❌ backend\Dockerfile is missing
)

if exist "frontend\Dockerfile" (
    echo ✅ frontend\Dockerfile exists
) else (
    echo ❌ frontend\Dockerfile is missing
)

if exist "frontend\nginx.conf" (
    echo ✅ frontend\nginx.conf exists
) else (
    echo ❌ frontend\nginx.conf is missing
)

if exist "DEPLOYMENT_GUIDE.md" (
    echo ✅ DEPLOYMENT_GUIDE.md exists
) else (
    echo ❌ DEPLOYMENT_GUIDE.md is missing
)

echo.
echo 🎯 Next Steps:
echo 1. Push your code to GitHub
echo 2. Set up MongoDB Atlas (free)
echo 3. Create Render account
echo 4. Follow the DEPLOYMENT_GUIDE.md
echo.
echo 📚 Read DEPLOYMENT_GUIDE.md for detailed instructions
echo 🌐 Your app will be available at:
echo    Frontend: https://mutual-fund-tracker-frontend.onrender.com
echo    Backend:  https://mutual-fund-tracker-backend.onrender.com
echo.
echo 🎉 Happy deploying!
pause
