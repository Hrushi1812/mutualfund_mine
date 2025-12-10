import os
from dotenv import load_dotenv
import requests

load_dotenv()


print("Script starting...")
def get_ticker_from_isin(isin):
    url = "https://api.openfigi.com/v3/mapping"
    api_key = os.getenv("OPENFIGI_API_KEY")
    headers = {
        'Content-Type': 'application/json'
    }
    if api_key:
        headers['X-OPENFIGI-APIKEY'] = api_key

    payload = [{"idType": "ID_ISIN", "idValue": isin}]
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and 'data' in data[0]:
                results = data[0]['data']
                # Prefer NSE (IN) then BSE (IB)
                for item in results:
                    if item.get('exchCode') == 'IN':
                        return item.get('ticker') + ".NS"
                for item in results:
                    if item.get('exchCode') == 'IB':
                        return item.get('ticker') + ".BO"
                        
                # Fallback to first available with mapping if possible
                if results:
                    ticker = results[0].get('ticker')
                    exch = results[0].get('exchCode')
                    if exch == 'IN':
                        return ticker + ".NS"
                    elif exch == 'IB':
                        return ticker + ".BO"
                    return ticker
    except Exception as e:
        print(f"Error resolving ISIN {isin}: {e}")
    
    return None


# Test List of ISINs
test_isins = {
    "Reliance": "INE002A01018", # Expect RELIANCE.NS
    "TCS": "INE467B01029",      # Expect TCS.NS
    "Infosys": "INE009A01021",  # Expect INFY.NS
    "ITC": "INE154A01025",      # Expect ITC.NS
    "HDFCBANK": "INE040A01034"  # Expect HDFCBANK.NS (Returns HDFCB)
}

print("\n--- Testing Multiple ISINs ---")
with open("figi_output.txt", "w") as f:
    for name, isin in test_isins.items():
        ticker = get_ticker_from_isin(isin)
        log_line = f"{name} ({isin}) -> {ticker}\n"
        print(log_line)
        f.write(log_line)
