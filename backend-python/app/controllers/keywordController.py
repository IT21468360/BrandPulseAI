from app.controllers.scrapeController import process_scraping
from app.controllers.preprocessController import process_preprocessing
from app.services.keyword.english.keywordExtractionService import extract_keywords
from app.services.keyword.english.databaseService import save_keywords_to_db
from fastapi import HTTPException

async def process_keywords(user_id, brand, url, dateRange, language):
    try:
        # ✅ Step 1: Scrape Content
        scrape_result = await process_scraping(url, dateRange)
        raw_content = scrape_result.get("scraped_content")
        if not raw_content:
            raise HTTPException(status_code=500, detail="Scraping failed or returned empty content.")

        # ✅ Step 2: Preprocess Text
        preprocess_result = await process_preprocessing(raw_content)
        cleaned_text = preprocess_result.get("preprocessed_content")
        if not cleaned_text:
            raise HTTPException(status_code=500, detail="Preprocessing failed or returned empty content.")

        # ✅ Step 3: Extract Keywords
        extracted_keywords = extract_keywords(cleaned_text, language)
        if not extracted_keywords:
            raise HTTPException(status_code=500, detail="Keyword extraction failed or returned no keywords.")

        # ✅ Step 4: Save Extracted Keywords to DB
        save_keywords_to_db(user_id, brand, url, extracted_keywords)

        return {"keywords": extracted_keywords}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
