from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from db import list_funds, delete_fund, client, create_user, get_user
from nav_logic import save_holdings_to_mongo, calculate_pnl, search_scheme_code
from auth import verify_password, get_password_hash, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mutual Fund NAV Estimator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_client():
    try:
        # Check connection
        client.admin.command('ismaster')
        print("\n✅ Connected to MongoDB successfully!\n")
    except Exception as e:
        print(f"\n❌ MongoDB Startup Error: {e}\n")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@app.post("/register")
def register(user: UserCreate):
    db_user = get_user(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    create_user(user.username, user.email, hashed_password)
    return {"message": "User created successfully"}

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def home():
    return {"message": "NAV Estimator API is running 🚀"}


@app.get("/funds/")
def view_funds(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    return {"funds_available": list_funds(user_id)}


@app.post("/upload-holdings/")
async def upload(
    fund_name: str = Form(...),
    scheme_code: str = Form(None), # Optional but recommended
    file: UploadFile = File(...),
    investment_type: str = Form(None), # 'lumpsum' or 'sip'
    invested_amount: str = Form(None), # Changed to str to handle empty strings
    invested_date: str = Form(None), # YYYY-MM-DD
    nickname: str = Form(None), # Optional nickname
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    # 1. Attempt to resolve Scheme Code if missing
    if not scheme_code:
        print(f"Searching scheme code for {fund_name}...")
        found_code = search_scheme_code(fund_name)
        if found_code:
            scheme_code = found_code
            print(f"Resolved {fund_name} -> {scheme_code}")

    # 2. Save Holdings
    save_result = save_holdings_to_mongo(fund_name, file, user_id, scheme_code, invested_amount, invested_date, nickname)
    
    # 3. If investment details provided, Calculate P&L immediately
    analysis = None
    
    # Parse amount safely
    amount_float = None
    if invested_amount and invested_amount.strip():
        try:
           amount_float = float(invested_amount)
        except ValueError:
           print(f"Invalid amount format: {invested_amount}")

    if amount_float and invested_date:
        try:
            analysis = calculate_pnl(fund_name, user_id, amount_float, invested_date)
        except Exception as e:
            print(f"Analysis failed: {e}")
            analysis = {"error": str(e)}

    return {
        "upload_status": save_result,
        "analysis": analysis,
        "scheme_code_used": scheme_code
    }

@app.post("/analyze-portfolio")
async def analyze_portfolio(
    fund_id: str = Form(...),
    investment_amount: float = Form(None),
    investment_date: str = Form(None), # YYYY-MM-DD
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes P&L for an existing fund in the DB.
    Triggers Live NAV estimation if market is open/data available.
    """
    user_id = str(current_user["_id"])
    result = calculate_pnl(fund_id, user_id, investment_amount, investment_date)
    return result

@app.delete("/funds/{fund_id}")
def remove_fund(fund_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    success = delete_fund(fund_id, user_id)
    if success:
        return {"message": f"Deleted fund {fund_id}"}
    return {"error": "Fund not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)