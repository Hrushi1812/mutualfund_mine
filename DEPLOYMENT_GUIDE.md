# 🚀 Render Deployment Guide for Mutual Fund Tracker

This guide will help you deploy your Mutual Fund Tracker app on Render for free.

## 📋 Prerequisites

1. **GitHub Account** - Your code should be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **MongoDB Atlas Account** - Free database hosting at [mongodb.com/atlas](https://mongodb.com/atlas)

## 🗄️ Step 1: Set up MongoDB Atlas (Free Database)

1. Go to [MongoDB Atlas](https://mongodb.com/atlas)
2. Create a free account
3. Create a new cluster (choose the free M0 tier)
4. Create a database user:
   - Go to "Database Access" → "Add New Database User"
   - Username: `mutual-fund-user`
   - Password: Generate a secure password
5. Whitelist IP addresses:
   - Go to "Network Access" → "Add IP Address"
   - Add `0.0.0.0/0` (allows access from anywhere)
6. Get your connection string:
   - Go to "Clusters" → "Connect" → "Connect your application"
   - Copy the connection string (it looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

## 🎯 Step 2: Deploy Backend on Render

1. **Connect GitHub Repository:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Backend Service:**
   - **Name**: `mutual-fund-tracker-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables:**
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/mutual_fund_tracker
   JWT_SECRET_KEY=your-super-secret-jwt-key-here
   ENVIRONMENT=production
   ```

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://mutual-fund-tracker-backend.onrender.com`)

## 🎨 Step 3: Deploy Frontend on Render

1. **Create Static Site:**
   - Go to Render Dashboard
   - Click "New" → "Static Site"
   - Connect your GitHub repository

2. **Configure Frontend Service:**
   - **Name**: `mutual-fund-tracker-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

3. **Set Environment Variables:**
   ```
   VITE_API_URL=https://mutual-fund-tracker-backend.onrender.com
   ```

4. **Deploy:**
   - Click "Create Static Site"
   - Wait for deployment to complete
   - Note your frontend URL (e.g., `https://mutual-fund-tracker-frontend.onrender.com`)

## 🔧 Step 4: Update CORS Settings

After both services are deployed, update your backend CORS settings:

1. Go to your backend service on Render
2. Go to "Environment" tab
3. Add/Update environment variable:
   ```
   CORS_ORIGINS=https://mutual-fund-tracker-frontend.onrender.com
   ```
4. Redeploy the backend service

## 🌐 Step 5: Custom Domain (Optional)

1. **Get a free domain:**
   - Use [Freenom](https://freenom.com) for free domains
   - Or use a subdomain from [No-IP](https://noip.com)

2. **Configure on Render:**
   - Go to your service settings
   - Add custom domain
   - Update DNS records as instructed

## 📱 Step 6: Test Your Deployment

1. **Test Backend:**
   - Visit: `https://your-backend-url.onrender.com`
   - Should see: `{"message": "Welcome to Mutual Fund Tracker API"}`

2. **Test Frontend:**
   - Visit: `https://your-frontend-url.onrender.com`
   - Should load your React app

3. **Test API Connection:**
   - Try logging in/registering
   - Upload a portfolio file
   - Check if data is saved to MongoDB

## 🚨 Important Notes

### Free Tier Limitations:
- **Backend**: Sleeps after 15 minutes of inactivity
- **Frontend**: No sleep time (static hosting)
- **Database**: 512MB storage limit
- **Build time**: 90 minutes per month

### Performance Tips:
1. **Keep backend awake**: Use [UptimeRobot](https://uptimerobot.com) to ping your backend every 14 minutes
2. **Optimize images**: Compress images before uploading
3. **Use CDN**: Consider Cloudflare for better performance

### Security:
1. **Change default JWT secret** in production
2. **Use environment variables** for all secrets
3. **Enable MongoDB authentication**
4. **Regular security updates**

## 🔄 Continuous Deployment

Your app will automatically redeploy when you push changes to your GitHub repository.

## 🆘 Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt
   - Verify Python version compatibility

2. **Database Connection Issues:**
   - Verify MongoDB connection string
   - Check IP whitelist in MongoDB Atlas
   - Ensure database user has proper permissions

3. **CORS Errors:**
   - Update CORS_ORIGINS environment variable
   - Include both HTTP and HTTPS URLs if needed

4. **Frontend Can't Connect to Backend:**
   - Verify VITE_API_URL environment variable
   - Check if backend is running (not sleeping)
   - Test backend URL directly

## 📞 Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **MongoDB Atlas Help**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## 🎉 Congratulations!

Your Mutual Fund Tracker app is now live on the internet! 🚀

**Your app URLs:**
- Frontend: `https://mutual-fund-tracker-frontend.onrender.com`
- Backend: `https://mutual-fund-tracker-backend.onrender.com`
- API Docs: `https://mutual-fund-tracker-backend.onrender.com/docs`
