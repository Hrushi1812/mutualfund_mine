
import difflib

def get_score(query, name):
    # Base similarity
    ratio = difflib.SequenceMatcher(None, query.lower(), name.lower()).ratio()
    
    # Existing Heuristics
    if "Direct" in name: ratio += 0.05
    if "Growth" in name: ratio += 0.05
    if "Regular" in name: ratio -= 0.05
    if "IDCW" in name or "Dividend" in name: ratio -= 0.05
    
    # PROPOSED: Penalty for Bonus
    if "Bonus" in name: ratio -= 0.05
    
    return ratio

def test():
    query = "Nippon India Multi Cap Fund - Direct Plan Growth Plan"
    
    options = [
        "Nippon India Multi Cap Fund - Direct Plan Growth Plan - Bonus Option",
        "Nippon India Multi Cap Fund - Direct Plan Growth Plan - Growth Option"
    ]
    
    print(f"Query: {query}\n")
    
    for opt in options:
        score = get_score(query, opt)
        print(f"Option: {opt}")
        print(f"Score: {score:.4f}")
        print("-" * 20)

if __name__ == "__main__":
    test()
