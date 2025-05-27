from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ✅ Named collections for clarity
english_collection = db["english_sentiment_predictions"]
sinhala_collection = db["sinhala_sentiment_predictions"]
