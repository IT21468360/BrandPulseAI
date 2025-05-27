
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# load the .env in your backend directory
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME   = os.getenv("DB_NAME", "BrandPulseAI")

<<<<<<< Updated upstream
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

=======
_client = None

def get_db():
    """
    Returns a singleton MongoClient database handle.
    """
    global _client
    if _client is None:
        # establish connection
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME]
>>>>>>> Stashed changes
