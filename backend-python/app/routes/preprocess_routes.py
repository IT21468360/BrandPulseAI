from fastapi import APIRouter, HTTPException, Request
from app.controllers.scrapeController import process_scraping  # ✅ Import scraping function
from app.controllers.preprocessController import process_preprocessing
import json

router = APIRouter()

@router.post("/preprocess")
async def preprocess_route(request: Request):
    """
    API endpoint for text preprocessing.
    """
    try:
        # ✅ Log the request payload
        data = await request.json()
        print("🟢 Received preprocessing request with payload:", json.dumps(data, indent=2))

        # ✅ Validate required fields
        required_keys = ["url", "dateRange"]
        if not all(key in data for key in required_keys):
            raise HTTPException(status_code=400, detail="❌ Missing required fields in request data.")

        url = data["url"]
        date_range = data["dateRange"]

        # ✅ First scrape the content (since raw content is not sent directly)
        scrape_result = await process_scraping(url, date_range)
        raw_content = scrape_result.get("scraped_content")
        if not raw_content:
            raise HTTPException(status_code=500, detail="❌ Scraping failed or returned empty content.")

        # ✅ Then preprocess the scraped content
        preprocess_result = await process_preprocessing(raw_content)

        return preprocess_result

    except Exception as e:
        print(f"❌ Error in preprocessing route: {e}")
        raise HTTPException(status_code=500, detail=str(e))
