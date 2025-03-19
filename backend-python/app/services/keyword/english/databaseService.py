import os
import time
from pymongo import MongoClient, errors
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Get MongoDB credentials from .env
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise ValueError("❌ Missing MongoDB configuration in .env file!")

# ✅ Initialize MongoDB Client with Retry Mechanism
MAX_RETRIES = 5
RETRY_DELAY = 2  # Seconds

def connect_to_mongo():
    for attempt in range(MAX_RETRIES):
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)  # 5 sec timeout
            client.server_info()  # Trigger exception if connection fails
            print("✅ Successfully connected to MongoDB!")
            return client
        except errors.ServerSelectionTimeoutError:
            print(f"⚠ Connection failed (Attempt {attempt+1}/{MAX_RETRIES})... Retrying in {RETRY_DELAY} sec")
            time.sleep(RETRY_DELAY)
    
    raise ConnectionError("❌ Could not connect to MongoDB after multiple attempts.")

# ✅ Establish Connection
client = connect_to_mongo()
db = client[DB_NAME]
keywords_collection = db["keywords"]  # ✅ Collection for storing extracted keywords

# ✅ Ensure Index on `user_id` for Faster Lookups
keywords_collection.create_index("user_id")

# ✅ Function to save extracted keywords
def save_keywords_to_db(user_id, brand, url, keywords):
    try:
        if not keywords:
            return "⚠ No keywords to save!"

        document = {
            "user_id": user_id,
            "brand": brand,
            "url": url,
            "keywords": keywords
        }
        
        # ✅ Upsert (Insert if not exists, update otherwise)
        result = keywords_collection.update_one(
            {"user_id": user_id, "brand": brand, "url": url},
            {"$set": document},
            upsert=True
        )

        if result.upserted_id:
            return "✅ Keywords inserted into MongoDB successfully!"
        else:
            return "✅ Keywords updated successfully!"

    except Exception as e:
        print(f"❌ Error saving keywords: {e}")
        return str(e)

# ✅ Function to retrieve keywords for a user
def get_keywords_by_user(user_id):
    try:
        data = list(keywords_collection.find({"user_id": user_id}, {"_id": 0}))
        if not data:
            return "⚠ No keywords found for the user."
        return data
    except Exception as e:
        print(f"❌ Error retrieving keywords: {e}")
        return []

# ✅ Function to clear all keywords (for testing)
def clear_keywords():
    try:
        result = keywords_collection.delete_many({})
        print(f"✅ Cleared {result.deleted_count} keywords in MongoDB!")
    except Exception as e:
        print(f"❌ Error clearing keywords: {e}")
