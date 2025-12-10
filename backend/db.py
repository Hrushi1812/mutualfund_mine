import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import InvalidURI, ConfigurationError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "mutual_funds")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "holdings")

import certifi

try:
    # Use certifi for explicit CA bundle (fixes SSL errors on some Windows/Mac setups)
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
except (InvalidURI, ConfigurationError) as e:
    print(f"\n❌ MongoDB Connection Error: {e}")
    print("👉 HINT: If you have special characters (like '@', ':', '%') in your password, you MUST 'URL Escape' them.")
    print("   Example: '@' becomes '%40', '+' becomes '%2B'.\n")
    # We don't exit here because local dev might work without auth, but for Atlas it will fail.
    # However, app.py imports objects from here. If client fails, app might crash later.
    # Let's let it crash but after printing the hint.
    raise e

db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]



def save_holdings(fund_name, holdings_list, scheme_code=None, invested_amount=None, invested_date=None):
    data = {
        "fund_name": fund_name,
        "holdings": holdings_list,
        "last_updated": True  # simplified timestamp
    }
    if scheme_code:
        data["scheme_code"] = scheme_code
    if invested_amount is not None:
        data["invested_amount"] = invested_amount
    if invested_date:
        data["invested_date"] = invested_date
        
    collection.update_one(
        {"fund_name": fund_name},
        {"$set": data},
        upsert=True,
    )


def get_holdings(fund_name):
    doc = collection.find_one({"fund_name": fund_name})
    # Return the full doc so we can access scheme_code
    return doc


def list_funds():
    return [doc["fund_name"] for doc in collection.find({}, {"fund_name": 1})]

def delete_fund(fund_name):
    result = collection.delete_one({"fund_name": fund_name})
    return result.deleted_count > 0
