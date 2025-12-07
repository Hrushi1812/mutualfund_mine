import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "mutual_funds")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "holdings")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]



def save_holdings(fund_name, holdings_list, scheme_code=None):
    data = {
        "fund_name": fund_name,
        "holdings": holdings_list,
        "last_updated": True  # simplified timestamp
    }
    if scheme_code:
        data["scheme_code"] = scheme_code
        
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
