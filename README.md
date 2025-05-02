# MutualFundTracker

Simple script to estimate a mutual fund's intraday NAV movement using component stock moves from Yahoo Finance.

## What this script does
- Reads holdings from `nav4.xlsx` (expects columns: `ISIN`, `Name of the Instrument`, `% to NAV`, `Symbol`).
- Fetches recent prices for each `Symbol` from Yahoo (yfinance).
- Computes each stock's daily % change and the weighted contribution to the fund (% to NAV * daily change).
- Estimates current NAV from user-provided previous NAV and returns a P&L summary.
- Writes detailed output to `fund_estimation_<timestamp>.xlsx`.
- Logs progress to console (DEBUG level).

## Files
- `app.py` — main script (reads `nav4.xlsx`, fetches prices, writes output).
- `nav4.xlsx` — input (you provide).
- `fund_estimation_<timestamp>.xlsx` — generated output.
- `mapping_fetch_debug.csv`, `unmapped_isins.csv` — (not used by this script) may appear if you use mapping helpers.

## Data persistance
- Input files are saved to a MongoDB database by the app. If no local input is provided, the script can load the latest saved holdings from the database so you don't need to re-upload daily.

## Input file format (nav4.xlsx)
The script expects these columns (case-sensitive):
- `ISIN` (optional but can be present)
- `Name of the Instrument`
- `% to NAV`
- `Symbol`  ← required for price fetch

Example rows (Excel):
| ISIN         | Name of the Instrument      | % to NAV | Symbol       |
|--------------|-----------------------------|----------:|--------------|
| INE040A01034 | HDFC Bank Limited           |     6.50  | HDFCBANK.NS  |
| INE009A01021 | Infosys Limited             |     3.25  | INFY.NS      |

If `Symbol` is missing, the script will drop that row.

## Requirements
- Python 3.10+ recommended
- Required packages (install into your venv):
  - pandas
  - yfinance
  - openpyxl (for Excel I/O)

Install example:
```powershell
python -m pip install pandas yfinance openpyxl
```

You can also use the provided `requirements.txt` if present.

## Usage
From project root (Windows PowerShell):
```powershell
python .\app.py
```
The script will:
1. Print and log columns found.
2. Ask for yesterday's NAV and your investment amount (console input).
3. Fetch prices and compute results.
4. Save the detailed report as an Excel file.

## Configurable items / quick edits
- Rate limiting: current pause between Yahoo requests is `time.sleep(0.4 + random.uniform(0, 0.4))` in `app.py`. Increase base value to reduce 429s.
- If you want mapping from ISIN → Symbol, add a mapping step (OpenFIGI or manual CSV) before running `app.py`. This script requires `Symbol` to be present.

## Common issues & troubleshooting
- "Not enough data points" or yfinance errors:
  - Symbol may be incorrect; ensure `Symbol` matches Yahoo ticker (e.g. `HDFCBANK.NS` for NSE).
  - Some instruments (non-equity, delisted) have no price data.
  - Rate limits: increase sleep delay or stagger runs.

- To open Excel in default app:
```powershell
Start-Process .\nav4.xlsx
```

## Output
- Excel file `fund_estimation_<timestamp>.xlsx` with:
  - Sheet `Details` — original rows plus `Daily Change (%)` and `Weighted Return`
  - Sheet `Summary` — NAV and P&L summary

## Future Implementations
- Add SIP along with the lumpsum

