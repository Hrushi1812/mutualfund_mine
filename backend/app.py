from fastapi import FastAPI, File, Form, UploadFile

from db import list_funds
from nav_logic import estimate_nav, save_holdings_to_mongo

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mutual Fund NAV Estimator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    file: UploadFile = File(...)
):
    return save_holdings_to_mongo(fund_name, file, scheme_code)


@app.post("/estimate-nav/")
async def estimate(
    fund_name: str = Form(...),
    investment: float = Form(...),
    input_date: str = Form(None), # YYYY-MM-DD
):
    # prev_nav is now fetched automatically
    return estimate_nav(fund_name, investment, input_date)
