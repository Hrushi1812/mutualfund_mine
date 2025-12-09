from fastapi import FastAPI, File, Form, UploadFile

from db import list_funds, delete_fund, client
from nav_logic import save_holdings_to_mongo, calculate_pnl, search_scheme_code

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

@app.get("/")
def home():
    return {"message": "NAV Estimator API is running 🚀"}


@app.get("/funds/")
def view_funds():
    return {"funds_available": list_funds()}


@app.post("/upload-holdings/")
async def upload(
    fund_name: str = Form(...),
    scheme_code: str = Form(None), # Optional but recommended
    file: UploadFile = File(...),
    investment_type: str = Form(None), # 'lumpsum' or 'sip'
    invested_amount: str = Form(None), # Changed to str to handle empty strings
    invested_date: str = Form(None), # YYYY-MM-DD
):
    # 1. Attempt to resolve Scheme Code if missing
    if not scheme_code:
        print(f"Searching scheme code for {fund_name}...")
        found_code = search_scheme_code(fund_name)
        if found_code:
            scheme_code = found_code
            print(f"Resolved {fund_name} -> {scheme_code}")

    # 2. Save Holdings
    save_result = save_holdings_to_mongo(fund_name, file, scheme_code)
    
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
            analysis = calculate_pnl(fund_name, amount_float, invested_date)
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
    fund_name: str = Form(...),
    investment_amount: float = Form(...),
    investment_date: str = Form(...) # YYYY-MM-DD
):
    """
    Analyzes P&L for an existing fund in the DB.
    Triggers Live NAV estimation if market is open/data available.
    """
    result = calculate_pnl(fund_name, investment_amount, investment_date)
    return result

@app.delete("/funds/{fund_name}")
def remove_fund(fund_name: str):
    success = delete_fund(fund_name)
    if success:
        return {"message": f"Deleted {fund_name}"}
    return {"error": "Fund not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)