
import requests
import difflib

def search_scheme_code_current(query):
    # Simulates current naive implementation
    try:
        url = f"https://api.mfapi.in/mf/search?q={query}"
        response = requests.get(url)
        if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Current logic matches this: takes the first one
                    return data[0]["schemeName"], str(data[0]["schemeCode"])
    except Exception as e:
        print(f"Error: {e}")
    return None, None

def search_scheme_code_improved(query):
    # Improved logic
    try:
        url = f"https://api.mfapi.in/mf/search?q={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data: return None, None
            
            # Helper to score match
            def get_score(item):
                name = item["schemeName"]
                # Base similarity
                ratio = difflib.SequenceMatcher(None, query.lower(), name.lower()).ratio()
                
                # Bonus for "Direct" and "Growth" if user query doesn't specify otherwise
                # (Assuming modern users prefer Direct Growth)
                if "Direct" in name: ratio += 0.05
                if "Growth" in name: ratio += 0.05
                if "Regular" in name: ratio -= 0.05
                if "IDCW" in name or "Dividend" in name: ratio -= 0.05
                
                return ratio

            best_match = max(data, key=get_score)
            return best_match["schemeName"], str(best_match["schemeCode"])

    except Exception as e:
        print(f"Error: {e}")
    return None, None

def test():
    test_cases = [
        "HDFC Top 100",
        "Quant Small Cap",
        "Parag Parikh Flexi Cap",
        "Nippon India Small Cap",
        "SBI Bluechip Fund"
    ]
    
    print(f"{'Query':<30} | {'Current Result':<40} | {'Improved Result':<40}")
    print("-" * 120)
    
    for q in test_cases:
        cur_name, cur_code = search_scheme_code_current(q)
        imp_name, imp_code = search_scheme_code_improved(q)
        
        # trim names for display
        c_disp = (cur_name[:37] + "...") if cur_name and len(cur_name) > 37 else str(cur_name)
        i_disp = (imp_name[:37] + "...") if imp_name and len(imp_name) > 37 else str(imp_name)
        
        print(f"{q:<30} | {c_disp:<40} | {i_disp:<40}")

if __name__ == "__main__":
    test()
