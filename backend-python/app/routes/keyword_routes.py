from fastapi import APIRouter, HTTPException, Request
from app.services.keyword.english.keywordExtractionService import process_full_extraction
from app.services.keyword.sinhala.keywordExtractionService import process_sinhala_extraction

import json

# ✅ Initialize API Router
router = APIRouter()

@router.post("/extract")
async def extract_keywords_route(request: Request):
    try:
        data = await request.json()
        print("🟢 Payload received:", json.dumps(data, indent=2))

        required_keys = ["user_id", "brand", "url", "dateRange", "language"]
        if not all(key in data for key in required_keys):
            raise HTTPException(status_code=400, detail="❌ Missing required fields in request data.")

        language = data["language"].lower()

        if language == "english":
            response = await process_full_extraction(
                data["user_id"],
                data["brand"],
                data["url"],
                data["dateRange"],
                data["language"]
            )
        elif language == "sinhala":
            response = await process_sinhala_extraction(
                data["user_id"],
                data["brand"],
                data["url"],
                data["dateRange"],
                data["language"]
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        print("✅ Keyword extraction complete. Returning response.")
        return response

    except Exception as e:
        print("❌ Error in extract_keywords_route:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Keyword Extraction Failed: {str(e)}")

