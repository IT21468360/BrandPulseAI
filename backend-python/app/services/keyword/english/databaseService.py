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
from datetime import datetime

def save_keywords_to_db(user_id, brand, url, language, date_range, keywords_df):
    try:
        if keywords_df is None or keywords_df.empty:
            return "⚠ No keywords to save!"

        # ✅ Extract only the 'Keyword' column as a list
        keyword_list = keywords_df["Keyword"].astype(str).tolist()
        now = datetime.utcnow()

        # Full match criteria
        query = {
            "user_id": user_id,
            "brand": brand,
            "url": url,
            "language": language,
            "dateRange.start": date_range["start"],
            "dateRange.end": date_range["end"]
        }

        existing = keywords_collection.find_one(query)

        if existing:
            keywords_collection.update_one(query, { "$set": { "KeywordList": keyword_list } })
            print("✅ Keywords updated in MongoDB.")
        else:
            doc = {
                "user_id": user_id,
                "brand": brand,
                "url": url,
                "language": language,
                "KeywordList": keyword_list,
                "dateRange": {
                    "start": date_range["start"],
                    "end": date_range["end"]
                },
                "created_at": now
            }
            keywords_collection.insert_one(doc)
            print("✅ Keywords inserted into MongoDB.")

    except Exception as e:
        print(f"❌ Error saving to DB: {e}")
        raise HTTPException(status_code=500, detail=f"MongoDB Save Failed: {str(e)}")


# ✅ Function to retrieve top 20 keywords for a user
def get_keywords_by_user(user_id):
    try:
        result = keywords_collection.find({"user_id": user_id})
        top_keywords_data = []

        for doc in result:
            # Only return top 20 keywords per document
            keywords_subset = doc.get("KeywordList", [])[:20]
            top_keywords_data.append({
                "brand": doc.get("brand"),
                "url": doc.get("url"),
                "language": doc.get("language"),
                "dateRange": doc.get("dateRange"),
                "keywords": keywords_subset
            })

        if not top_keywords_data:
            return "⚠ No keywords found for the user."

        return top_keywords_data
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
