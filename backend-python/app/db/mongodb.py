
from pymongo import MongoClient
import os

# ✅ Load MongoDB config
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

# ✅ Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

<<<<<<< Updated upstream
=======
# ✅ Named collections for clarity
english_collection = db["english_sentiment_predictions"]
sinhala_collection = db["sinhala_sentiment_predictions"]

# # ✅ General-purpose save function (works for any collection)
# def save_predictions_to_db(data, target_collection):
#     if isinstance(data, list) and data:
#         target_collection.insert_many(data)
#     elif isinstance(data, dict):
#         target_collection.insert_one(data)
>>>>>>> Stashed changes
