from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, portfolio
from app.config import settings
import os

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="API for tracking mutual fund portfolios"
)

# CORS middleware - configured for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (React app)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# API routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

# API root route
@app.get("/api")
async def api_root():
    return {"message": "Welcome to Mutual Fund Tracker API"}

# Serve React app for all non-API routes
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # Don't serve React app for API routes
    if full_path.startswith(("api", "auth", "portfolio", "docs", "openapi.json")):
        return {"error": "Not found"}
    
    # Serve index.html for all other routes (React Router)
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"message": "Frontend not built yet. Run 'npm run build' in frontend directory."}

@app.on_event("startup")
async def startup_db_client():
    print("Connecting to MongoDB...")
    await connect_to_mongo()
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    print("Closing MongoDB connection...")
    await close_mongo_connection()
    print("MongoDB connection closed")
