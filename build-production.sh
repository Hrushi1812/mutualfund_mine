#!/bin/bash

# 🚀 Production Build Script for Render Deployment
set -e  # Exit on any error

echo "🚀 Starting production build..."

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

# Show versions for debugging
echo "🔍 Environment info:"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo "Current directory: $(pwd)"

# Build frontend
echo "🔨 Building frontend..."
npm run build

# Verify build
echo "✅ Verifying build..."
if [ ! -d "dist" ]; then
    echo "❌ Build failed - dist directory not found"
    exit 1
fi

echo "📁 Build contents:"
ls -la dist/

# Create backend static directory
echo "📁 Creating backend static directory..."
mkdir -p ../backend/static

# Copy files
echo "📋 Copying files..."
cp -r dist/* ../backend/static/

# Verify copy
echo "✅ Verifying copy..."
if [ ! -f "../backend/static/index.html" ]; then
    echo "❌ Copy failed - index.html not found"
    exit 1
fi

echo "📁 Static directory contents:"
ls -la ../backend/static/

echo "🎉 Build completed successfully!"
