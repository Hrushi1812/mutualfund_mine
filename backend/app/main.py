from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, portfolio

app = FastAPI(title="Mutual Fund Tracker API")

# CORS middleware - adjust allow_origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL(s) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to Mutual Fund Tracker API"}

# Include routers with prefixes and tags for better API docs organization
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

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
