from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.controllers.youtube_scraper_controller import scrape_and_classify_to_mongo_and_csv

router = APIRouter()

class ScrapeRequest(BaseModel):
    start_date: str  # format: "YYYY-MM-DD"
    end_date: str

@router.post("/aspect/scrape")
def run_youtube_aspect_scraper(input: ScrapeRequest):
    try:
        result = scrape_and_classify_to_mongo_and_csv(input.start_date, input.end_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
