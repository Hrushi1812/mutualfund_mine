import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import InvalidURI, ConfigurationError
from bson import ObjectId

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "mutual_funds")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "holdings")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")

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
users_collection = db[USERS_COLLECTION]

def create_user(username, email, hashed_password):
    user = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": "now" # In real app use datetime
    }
    try:
        users_collection.insert_one(user)
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user(username):
    return users_collection.find_one({"username": username})



def save_holdings(fund_name, holdings_list, user_id, scheme_code=None, invested_amount=None, invested_date=None, nickname=None):
    data = {
        "fund_name": fund_name,
        "holdings": holdings_list,
        "user_id": user_id,
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
        "user_id": user_id,
        "invested_amount": invested_amount,
        "invested_date": invested_date
    }

    collection.update_one(
        query,
        {"$set": data},
        upsert=True,
    )


def get_holdings(fund_id_str, user_id=None):
    try:
        if isinstance(fund_id_str, str):
            oid = ObjectId(fund_id_str)
        else:
            oid = fund_id_str
        doc = collection.find_one({"_id": oid})
        # If user_id is provided, verify ownership explicitly
        if user_id and doc:
            if doc.get("user_id") != user_id:
                return None
        return doc
    except:
        return None


def list_funds(user_id):
    if not user_id:
        return []
    cursor = collection.find({"user_id": user_id}, {"fund_name": 1, "invested_amount": 1, "invested_date": 1, "scheme_code": 1, "nickname": 1})
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

def delete_fund(fund_id_str, user_id):
    try:
        # Only delete if user_id matches
        res = collection.delete_one({"_id": ObjectId(fund_id_str), "user_id": user_id})
        return res.deleted_count > 0
    except:
        return False
