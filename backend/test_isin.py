import requests

def get_ticker_from_isin(isin):
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={isin}&quotesCount=1&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        data = r.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            return data['quotes'][0]['symbol']
    except Exception as e:
        print(e)
    return None

# Test with HDFC Bank ISIN
isin = "INE040A01034"
print(f"{isin} -> {get_ticker_from_isin(isin)}")
