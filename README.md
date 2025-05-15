# MutualFundTracker

A FinTech backend system that estimates the current-day NAV (Net Asset Value) of a mutual fund in real time using live stock price data from Yahoo Finance.

This solves the problem where daily NAV is announced after market close, but investors want to know their live P&L and current portfolio worth during the trading day.

## What this script does
- Upload mutual fund holdings once using Excel
- Holdings stored securely in MongoDB
- Fetches live stock prices using Yahoo Finance 
- Estimates NAV change based on portfolio weight %
- Calculates current value & P&L of investor holdings

## 🛠 Tech Stack

| Layer              | Technology |
|--------------------|------------|
| Backend            | FastAPI    |
| Database           | MongoDB    |
| Financial Data API | yfinance   |
| Language           | Python     |
| API Server         | Uvicorn    |

## Project structure

project/
├─ app.py # FastAPI backend API
├─ nav_logic.py # NAV calculation logic
├─ db.py # Mongo helper functions
├─ requirements.txt # Package dependencies
├─ .env # Environment variables

## Environmental Setup

create a '.env' file:
```powershell
MONGO_URI=mongodb://localhost:27017
MONGO_DB=mutual_funds
MONGO_COLLECTION=holdings
```

## Installation And Run
```bash
git clone <repo-url>
cd project
pip install -r requirements.txt
uvicorn app:app --reload
```
## How it works
- Reads MF holdings
- Fetches individual stock price movement → last 2 days
- Calculates % change for each stock
- Multiplies change with stock’s % weight in NAV
- Sums all weighted returns → estimated NAV change
- Computes investor P&L instantly

## Challenges solved
- Mutual fund NAV not available during market hours
- Live price fetching rate limits handled via staggered requests
- Persistent storage so users upload holdings only once
- Modular architecture for future features (UI, auth, deployment)

## Future Implementations
- Add SIP along with the lumpsum

