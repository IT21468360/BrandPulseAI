import os
import json
import pandas as pd
import traceback
from fastapi import HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv

from app.services.keyword.sinhala.scraperService import scrape_content
from app.services.keyword.sinhala.preprocessService import preprocess_content
from app.services.keyword.sinhala.databaseService import save_keywords_to_db
from app.services.keyword.sinhala.XLMR_keyBERTService import run_keybert_extraction

# ✅ Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "keywords"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ✅ Main Sinhala Keyword Extraction Pipeline
async def process_sinhala_extraction(user_id, brand, url, dateRange, language):
    try:
        folder_path = os.path.join("data", "keyword", "sinhala")
        keybert_path = os.path.join(folder_path, "KeyBERT_keywords.json")
        vocab_path = os.path.join(folder_path, "sinhala_financial_vocab.json")

        # Step 1: Scrape and preprocess
        scrape_result = await scrape_content(url, dateRange)
        if not scrape_result or "scraped_content" not in scrape_result:
            raise HTTPException(status_code=500, detail="Scraping failed. No content returned.")

        if not await preprocess_content():
            raise HTTPException(status_code=500, detail="Preprocessing failed. No processed content.")

        # Step 2: Extract keywords
        if not run_keybert_extraction():
            raise HTTPException(status_code=500, detail="KeyBERT extraction failed.")

        # Step 3: Filter with Financial Vocabulary
        filtered_keywords_df = filter_keywords_with_vocab(keybert_path, vocab_path)
        if filtered_keywords_df.empty:
            return {"message": "No valid financial keywords extracted."}

        # Step 4: Save final results
        save_final_keywords(user_id, brand, url, language, dateRange, filtered_keywords_df)
        save_keywords_to_db(user_id, brand, url, language, dateRange, filtered_keywords_df)

        return {
            "success": True,
            "message": "Filtered financial keywords extracted and saved successfully!",
            "keywords": filtered_keywords_df["Keyword"].tolist()
        }

    except Exception as e:
        print("❌ Error in Sinhala pipeline:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Keyword Extraction Failed: {str(e)}")


# ✅ Filter KeyBERT keywords using financial vocabulary
def filter_keywords_with_vocab(keybert_file_path, vocab_file_path):
    try:
        with open(keybert_file_path, "r", encoding="utf-8") as f:
            keybert_data = json.load(f)

        with open(vocab_file_path, "r", encoding="utf-8") as f:
            financial_vocab = set(json.load(f))  # List to set

        keyword_set = set()
        for item in keybert_data:
            keywords = item.get("keywords", [])
            if isinstance(keywords, str):
                keywords = json.loads(keywords)
            for kw in keywords:
                if kw in financial_vocab:
                    keyword_set.add(kw)

        return pd.DataFrame(list(keyword_set), columns=["Keyword"])

    except Exception as e:
        print(f"❌ Error filtering keywords: {e}")
        return pd.DataFrame(columns=["Keyword"])


# ✅ Save final keywords as JSON
def save_final_keywords(user_id, brand, url, language, dateRange, keywords_df):
    FINAL_KEYWORDS_FILE = os.path.join("data", "keyword", "sinhala", "final_boosted_keywords.json")
    final_data = {
        "user_id": user_id,
        "brand": brand,
        "url": url,
        "language": language,
        "KeywordList": keywords_df["Keyword"].tolist(),
        "dateRange": dateRange
    }

    with open(FINAL_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Final keywords saved to {FINAL_KEYWORDS_FILE}")
