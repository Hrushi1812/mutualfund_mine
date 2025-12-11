import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import InvalidURI, ConfigurationError
from bson import ObjectId

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



def save_holdings(fund_name, holdings_list, scheme_code=None, invested_amount=None, invested_date=None, nickname=None):
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
    if nickname:
        data["nickname"] = nickname
        
    # Composite key for uniqueness: Name + Amount + Date to allow duplicates of name
    query = {
        "fund_name": fund_name,
        "invested_amount": invested_amount,
        "invested_date": invested_date
    }

    collection.update_one(
        query,
        {"$set": data},
        upsert=True,
    )


def get_holdings(fund_id_str):
    try:
        if isinstance(fund_id_str, str):
            oid = ObjectId(fund_id_str)
        else:
            oid = fund_id_str
        doc = collection.find_one({"_id": oid})
        return doc
    except:
        return None


def list_funds():
    cursor = collection.find({}, {"fund_name": 1, "invested_amount": 1, "invested_date": 1, "scheme_code": 1, "nickname": 1})
    funds = []
    for doc in cursor:
        funds.append({
            "id": str(doc["_id"]),
            "fund_name": doc.get("fund_name"),
            "invested_amount": doc.get("invested_amount"),
            "invested_date": doc.get("invested_date"),
            "scheme_code": doc.get("scheme_code"),
            "nickname": doc.get("nickname")
        })
    return funds

def delete_fund(fund_id_str):
    try:
        res = collection.delete_one({"_id": ObjectId(fund_id_str)})
        return res.deleted_count > 0
    except:
        return False
