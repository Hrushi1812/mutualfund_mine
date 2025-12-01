from fastapi import FastAPI, File, Form, UploadFile

from db import list_funds
from nav_logic import estimate_nav, save_holdings_to_mongo

app = FastAPI(title="Mutual Fund NAV Estimator API")


@app.get("/")
def home():
    return {"message": "NAV Estimator API is running 🚀"}


@app.get("/funds/")
def view_funds():
    return {"funds_available": list_funds()}


@app.post("/upload-holdings/")
async def upload(fund_name: str = Form(...), file: UploadFile = File(...)):
    return save_holdings_to_mongo(fund_name, file)


@app.post("/estimate-nav/")
async def estimate(
    fund_name: str = Form(...),
    prev_nav: float = Form(...),
    investment: float = Form(...),
):
    return estimate_nav(fund_name, prev_nav, investment)
