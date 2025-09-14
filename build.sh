#!/bin/bash

# 🚀 Build script for Mutual Fund Tracker - Combined Deployment
echo "🚀 Starting build process..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Navigate to frontend directory
echo "📁 Navigating to frontend directory..."
cd frontend

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Frontend dependencies installation failed"
    exit 1
fi

# Build frontend
echo "🔨 Building frontend..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Frontend build failed - dist directory not found"
    echo "📋 Checking for build errors..."
    ls -la
    exit 1
fi

echo "✅ Frontend build successful"

# Create backend static directory
echo "📁 Creating backend static directory..."
mkdir -p ../backend/static

# Copy built files
echo "📋 Copying built files..."
cp -r dist/* ../backend/static/

# Verify files were copied
if [ -f "../backend/static/index.html" ]; then
    echo "✅ Files copied successfully"
    echo "📋 Static files:"
    ls -la ../backend/static/
else
    echo "❌ Failed to copy files"
    exit 1
fi

echo "🎉 Build completed successfully!"
