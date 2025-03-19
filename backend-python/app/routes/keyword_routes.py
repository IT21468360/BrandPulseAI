from fastapi import APIRouter, HTTPException, Request
from app.services.keyword.english.keywordExtractionService import process_full_extraction
import json

# ✅ Initialize API Router
router = APIRouter()

@router.post("/extract")
async def extract_keywords_route(request: Request):
    """
    API endpoint to trigger full pipeline: Scrape → Preprocess → Extract → Save to DB.
    """
    try:
        # ✅ Log the request payload
        data = await request.json()
        print("🟢 Received keyword extraction request with payload:", json.dumps(data, indent=2))

        required_keys = ["user_id", "brand", "url", "dateRange", "language"]
        if not all(key in data for key in required_keys):
            raise HTTPException(status_code=400, detail="❌ Missing required fields in request data.")

        response = await process_full_extraction(data["user_id"], data["brand"], data["url"], data["dateRange"], data["language"])

        return response

    except Exception as e:
        print(f"❌ Error in extract_keywords_route: {e}")
        raise HTTPException(status_code=500, detail=str(e))
