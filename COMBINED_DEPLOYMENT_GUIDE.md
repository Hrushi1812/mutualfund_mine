# 🚀 Combined Deployment Guide for Mutual Fund Tracker

## 🎯 **What is Combined Deployment?**

Your **frontend (React)** and **backend (FastAPI)** will be deployed as **one single service** on Render. This means:
- ✅ **One URL** for everything
- ✅ **No CORS issues**
- ✅ **Simpler setup**
- ✅ **Easier to manage**

## 📋 **Prerequisites**

1. **GitHub Repository** - Your code pushed to GitHub
2. **MongoDB Atlas** - Free database (already set up)
3. **Render Account** - Sign up at [render.com](https://render.com)

## 🗄️ **MongoDB Atlas Setup (If Not Done)**

1. **Get Connection String:**
   - Go to MongoDB Atlas → Clusters → Connect
   - Choose "Connect your application"
   - **Driver:** Python
   - **Version:** 3.6 or later
   - Copy the connection string

2. **Add Database Name:**
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/mutual_fund_tracker
   ```

## 🚀 **Deploy on Render (Single Service)**

### **Step 1: Create Web Service**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository

### **Step 2: Configure Service**
- **Name:** `mutual-fund-tracker-combined`
- **Environment:** `Python 3`
- **Region:** Choose closest to you
- **Branch:** `main` (or your default branch)

### **Step 3: Build & Start Commands**
- **Build Command:**
  ```bash
  pip install -r backend/requirements.txt && cd frontend && npm install && npm run build && mkdir -p backend/static && cp -r frontend/dist/* backend/static/
  ```
- **Start Command:**
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### **Step 4: Environment Variables**
Add these environment variables:

```
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/mutual_fund_tracker
JWT_SECRET_KEY=your-super-secret-jwt-key-here
ENVIRONMENT=production
PYTHON_VERSION=3.9.18
```

### **Step 5: Deploy**
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your app will be available at: `https://mutual-fund-tracker-combined.onrender.com`

## 🎉 **Your App URLs**

After deployment, everything will be available at **one URL**:

- **Frontend:** `https://mutual-fund-tracker-combined.onrender.com`
- **Backend API:** `https://mutual-fund-tracker-combined.onrender.com/api`
- **API Documentation:** `https://mutual-fund-tracker-combined.onrender.com/docs`
- **Auth Endpoints:** `https://mutual-fund-tracker-combined.onrender.com/auth`
- **Portfolio Endpoints:** `https://mutual-fund-tracker-combined.onrender.com/portfolio`

## 🔧 **How It Works**

### **Build Process:**
1. **Install Python dependencies** from `backend/requirements.txt`
2. **Install Node.js dependencies** from `frontend/package.json`
3. **Build React app** using `npm run build`
4. **Copy built files** to `backend/static/` directory
5. **Start FastAPI server** which serves both API and static files

### **Runtime:**
- **API requests** (like `/auth/login`) → Handled by FastAPI
- **Static files** (like `/`, `/dashboard`) → Served by FastAPI from `static/` directory
- **React Router** → All non-API routes serve `index.html`

## ✅ **Testing Your Deployment**

### **1. Test Frontend:**
- Visit: `https://your-app-name.onrender.com`
- Should load your React app

### **2. Test API:**
- Visit: `https://your-app-name.onrender.com/api`
- Should return: `{"message": "Welcome to Mutual Fund Tracker API"}`

### **3. Test Full Functionality:**
- Try user registration/login
- Upload portfolio file
- Check if data saves to MongoDB

## 🆘 **Troubleshooting**

### **Build Fails:**
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt` and `package.json`
- Verify Python and Node.js versions

### **App Doesn't Load:**
- Check if build completed successfully
- Verify static files were copied to `backend/static/`
- Check Render logs for errors

### **API Not Working:**
- Verify MongoDB connection string
- Check environment variables are set correctly
- Test API endpoints directly

### **Database Connection Issues:**
- Verify MongoDB Atlas IP whitelist (0.0.0.0/0)
- Check database user permissions
- Ensure connection string includes database name

## 🎯 **Advantages of Combined Deployment**

✅ **Simpler Setup** - One service instead of two  
✅ **No CORS Issues** - Same origin for frontend and backend  
✅ **Easier Debugging** - All logs in one place  
✅ **Single URL** - Everything accessible from one domain  
✅ **Faster Development** - Single deployment process  

## 📊 **Free Tier Limits**

- **750 hours/month** - Enough for small apps
- **Sleeps after 15 minutes** of inactivity
- **512MB RAM** - Sufficient for your app
- **Automatic HTTPS** - SSL certificates included

## 🔄 **Keep Your App Awake (Optional)**

To prevent your app from sleeping:

1. **Use UptimeRobot:**
   - Go to [uptimerobot.com](https://uptimerobot.com)
   - Create free account
   - Add monitor for your app URL
   - Set interval to 14 minutes

2. **Or use cron-job.org:**
   - Set up a cron job to ping your app every 14 minutes

## 🎉 **Congratulations!**

Your Mutual Fund Tracker app is now live on the internet! 🚀

**Your app URL:** `https://mutual-fund-tracker-combined.onrender.com`

## 📞 **Need Help?**

- **Render Documentation:** [render.com/docs](https://render.com/docs)
- **MongoDB Atlas Help:** [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **FastAPI Documentation:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
