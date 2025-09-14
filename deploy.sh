#!/bin/bash

# 🚀 Mutual Fund Tracker - Render Deployment Script
# This script helps prepare your app for deployment on Render

echo "🚀 Preparing Mutual Fund Tracker for Render deployment..."

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project structure verified"

# Create production environment file
echo "📝 Creating production environment template..."
cat > backend/.env.production << EOF
# Production Environment Variables for Render
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/mutual_fund_tracker
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://mutual-fund-tracker-frontend.onrender.com
EOF

echo "✅ Production environment file created"

# Check if all required files exist
echo "🔍 Checking deployment files..."

required_files=(
    "render.yaml"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "frontend/nginx.conf"
    "DEPLOYMENT_GUIDE.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
    fi
done

echo ""
echo "🎯 Next Steps:"
echo "1. Push your code to GitHub"
echo "2. Set up MongoDB Atlas (free)"
echo "3. Create Render account"
echo "4. Follow the DEPLOYMENT_GUIDE.md"
echo ""
echo "📚 Read DEPLOYMENT_GUIDE.md for detailed instructions"
echo "🌐 Your app will be available at:"
echo "   Frontend: https://mutual-fund-tracker-frontend.onrender.com"
echo "   Backend:  https://mutual-fund-tracker-backend.onrender.com"
echo ""
echo "🎉 Happy deploying!"
