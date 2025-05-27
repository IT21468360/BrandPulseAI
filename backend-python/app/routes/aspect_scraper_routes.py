from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.controllers.youtube_scraper_controller import scrape_and_classify_to_mongo_and_csv
import traceback

router = APIRouter()

@router.get("/aspect/scrape")
async def trigger_scraping(start_date: str = Query(...), end_date: str = Query(...)):
    try:
        print("🔍 Start scraping from", start_date, "to", end_date)
        result = scrape_and_classify_to_mongo_and_csv(start_date, end_date)

        if not isinstance(result, dict):
            print("❌ Invalid response format from scraper:", result)
            return JSONResponse(status_code=500, content={"error": "Invalid result format."})

        if result.get("status") == "error":
            print("❌ Scraper returned error:", result)
            return JSONResponse(status_code=500, content=result)

        return JSONResponse(content=result)

    except Exception as e:
        print("🔥 Exception in scraping route:")
        traceback.print_exc()  # full error log
        return JSONResponse(status_code=500, content={"error": str(e)})
