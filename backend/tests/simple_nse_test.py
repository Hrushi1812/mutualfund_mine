
import requests

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/"
}

NSE_BASE_URL = "https://www.nseindia.com"
NSE_API_URL = "https://www.nseindia.com/api/quote-equity"

def test_nse(visit_home=False):
    print(f"Testing NSE fetch (visit_home={visit_home})...")
    s = requests.Session()
    s.headers.update(NSE_HEADERS)
    
    if visit_home:
        print(f"Visiting {NSE_BASE_URL} to set cookies...")
        try:
            s.get(NSE_BASE_URL, timeout=10)
            print("Cookies set:", s.cookies.get_dict())
        except Exception as e:
            print(f"Failed to visit home: {e}")

    print(f"Fetching {NSE_API_URL} for SBIN...")
    try:
        r = s.get(NSE_API_URL, params={"symbol": "SBIN"}, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
        if r.status_code == 200 and "application/json" in r.headers.get("Content-Type", ""):
            print("Success!")
        else:
            print("Failed.")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

if __name__ == "__main__":
    test_nse(visit_home=False) # Expect failure
    test_nse(visit_home=True)  # Expect success
