from fastapi import APIRouter, HTTPException
from app.services.keyword.english.databaseService import get_keywords_by_user, save_keywords_to_db, clear_keywords

# ✅ Initialize API Router
router = APIRouter()

# ✅ API: Get keywords for a user
@router.get("/keywords/{user_id}")
async def fetch_user_keywords(user_id: str):
    """
    Fetches extracted keywords for a given user.
    """
    try:
        data = get_keywords_by_user(user_id)
        if not data:
            return {"message": "⚠ No keywords found for this user."}
        return {"success": True, "keywords": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error fetching keywords: {str(e)}")

# ✅ API: Save keywords manually (for debugging)
@router.post("/keywords/save")
async def save_keywords(data: dict):
    """
    Saves extracted keywords to MongoDB.
    """
    try:
        required_keys = ["user_id", "brand", "url", "keywords"]
        if not all(key in data for key in required_keys):
            raise HTTPException(status_code=400, detail="❌ Missing required fields in request data.")

        response = save_keywords_to_db(data["user_id"], data["brand"], data["url"], data["keywords"])
        return {"success": True, "message": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error saving keywords: {str(e)}")

# ✅ API: Clear all keywords (FOR TESTING ONLY)
@router.delete("/keywords/clear")
async def delete_all_keywords():
    """
    Clears all extracted keywords (use with caution!).
    """
    try:
        clear_keywords()
        return {"success": True, "message": "✅ All keywords cleared!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error clearing keywords: {str(e)}")
