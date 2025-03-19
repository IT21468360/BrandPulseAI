from app.services.keyword.english.scraperService import scrape_content
from fastapi import HTTPException

async def process_scraping(url, dateRange):
    try:
        # ✅ Scrape Content
        raw_content = scrape_content(url, dateRange)
        if not raw_content:
            raise HTTPException(status_code=500, detail="Scraping failed or returned empty content.")

        return {"scraped_content": raw_content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
