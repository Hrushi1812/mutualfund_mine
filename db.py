from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "mutual_funds")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "holdings")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]


def save_holdings(fund_name, holdings_list):
    collection.update_one(
        {"fund_name": fund_name},
        {"$set": {"fund_name": fund_name, "holdings": holdings_list}},
        upsert=True
    )


def get_holdings(fund_name):
    doc = collection.find_one({"fund_name": fund_name})
    if doc:
        return doc.get("holdings", [])
    return None


def list_funds():
    return [doc["fund_name"] for doc in collection.find({}, {"fund_name": 1})]
