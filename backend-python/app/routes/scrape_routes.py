from fastapi import APIRouter, HTTPException, Request
from app.services.keyword.english.scraperService import scrape_content
import json

router = APIRouter()

@router.post("/scrape")
async def scrape_route(request: Request):
    """
    API endpoint to receive scraping requests and call `scrape_content`.
    """
    try:
        # ✅ Log and extract request data
        data = await request.json()
        print("🟢 Received scraping request:", json.dumps(data, indent=2))

        # ✅ Call the scraper function from `scraperService.py`
        scraped_content = await scrape_content(data)

        if not scraped_content:
            raise HTTPException(status_code=500, detail="❌ Scraping failed or returned no content.")

        return {"success": True, "scraped_content": scraped_content}

    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
