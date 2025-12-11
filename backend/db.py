import os
import certifi
from pymongo import MongoClient
from pymongo.errors import InvalidURI, ConfigurationError
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

try:
    # Use certifi for explicit CA bundle (fixes SSL errors on some Windows/Mac setups)
    client = MongoClient(settings.MONGO_URI, tlsCAFile=certifi.where())
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("✅ Connected to MongoDB successfully!")
except (InvalidURI, ConfigurationError) as e:
    print(f"\n❌ MongoDB Connection Error: {e}")
    print("👉 HINT: If you have special characters (like '@', ':', '%') in your password, you MUST 'URL Escape' them.")
    print("   Example: '@' becomes '%40', '+' becomes '%2B'.\n")
    raise e

db = client[settings.MONGO_DB]
holdings_collection = db["holdings"]
users_collection = db["users"]
