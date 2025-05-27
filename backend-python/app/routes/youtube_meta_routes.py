from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import os

router = APIRouter()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME", "BrandPulseAI")]

@router.get("/api/youtube/meta")
async def get_meta_data(brand: str):
    try:
        collection = db["youtube_meta_data"]
        query = {"title": {"$regex": brand, "$options": "i"}}
        results = list(collection.find(query, {
            "_id": 0,
            "title": 1,
            "description": 1,
            "url": 1,
            "likes": 1,
            "views": 1,
            "comment_count": 1,
            "published_at": 1,
            "hashtags": 1,
            "keyword_hits": 1
        }))
        return JSONResponse(content=results)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
