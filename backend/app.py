from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, holdings, portfolio
from db import client

app = FastAPI(title="Mutual Fund NAV Estimator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
def startup_db_client():
    try:
        client.admin.command('ismaster')
        print("\n✅ Connected to MongoDB successfully!\n")
    except Exception as e:
        print(f"\n❌ MongoDB Startup Error: {e}\n")

# Routes
app.include_router(auth.router)
app.include_router(holdings.router)
app.include_router(portfolio.router)

@app.get("/")
def home():
    return {"message": "NAV Estimator API is running 🚀 (Refactored)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)