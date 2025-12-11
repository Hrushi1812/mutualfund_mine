from datetime import datetime, time, timedelta, timezone
import pytz

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

# Market Timings
MARKET_OPEN_TIME = time(9, 15)
MARKET_CLOSE_TIME = time(15, 30)

# Simple static holiday list for 2024-2025 (Example - should be dynamic in prod)
# Format: YYYY-MM-DD
NSE_HOLIDAYS = {
    "2024-01-26", "2024-03-08", "2024-03-25", "2024-04-11", "2024-04-17",
    "2024-05-01", "2024-05-20", "2024-06-17", "2024-07-17", "2024-08-15",
    "2024-10-02", "2024-11-01", "2024-11-15", "2024-12-25",
    "2025-01-26", "2025-08-15", "2025-10-02", "2025-12-25"
}

def get_current_ist_time():
    """Returns current time in IST."""
    return datetime.now(IST)

def is_market_open(current_dt=None):
    """
    Checks if NSE market is currently open.
    """
    if not current_dt:
        current_dt = get_current_ist_time()
    
    # Check Weekend
    if current_dt.weekday() >= 5: # 5=Sat, 6=Sun
        return False

    # Check Holiday
    date_str = current_dt.strftime("%Y-%m-%d")
    if date_str in NSE_HOLIDAYS:
        return False

    # Check Time
    current_time = current_dt.time()
    return MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME

def is_trading_day(dt_obj=None):
    """Checks if the given date is a valid trading day (Mon-Fri, not holiday)."""
    if not dt_obj:
        dt_obj = get_current_ist_time()
    
    # Check Weekend
    if dt_obj.weekday() >= 5: return False
    
    # Check Holiday
    date_str = dt_obj.strftime("%Y-%m-%d")
    if date_str in NSE_HOLIDAYS: return False
    
    return True

def get_previous_business_day(ref_date=None):
    """
    Returns the date of the previous valid business day.
    """
    if not ref_date:
        ref_date = get_current_ist_time().date()
    
    check_date = ref_date - timedelta(days=1)
    
    # Loop back until we find a business day
    while True:
        # Check Weekend
        if check_date.weekday() >= 5:
            check_date -= timedelta(days=1)
            continue
            
        # Check Holiday
        if check_date.strftime("%Y-%m-%d") in NSE_HOLIDAYS:
             check_date -= timedelta(days=1)
             continue
        
        return check_date

def format_date_for_api(dt_obj):
    """Formats date as DD-MM-YYYY for MFAPI."""
    return dt_obj.strftime("%d-%m-%Y")

def parse_date_from_str(date_str):
    """Parses various date formats safely."""
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {date_str}")
