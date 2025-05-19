import os
import json
import pandas as pd
import traceback
from collections import defaultdict
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

        # Step 1: Scrape and preprocess
        scrape_result = await scrape_content(url, dateRange)
        if not scrape_result or "scraped_content" not in scrape_result:
            raise HTTPException(status_code=500, detail="Scraping failed. No content returned.")

        if not await preprocess_content():
            raise HTTPException(status_code=500, detail="Preprocessing failed. No processed content.")

        # Step 2: Extract keywords
        if not run_keybert_extraction():
            raise HTTPException(status_code=500, detail="KeyBERT extraction failed.")


        # Step 3: Score and rank keywords from JSON
        keywords_df = score_and_rank_keywords(folder_path)
        if keywords_df.empty:
            return { "message": "No keywords extracted." }

        # Step 4: Save to DB and JSON
        save_final_keywords(user_id, brand, url, language, dateRange, keywords_df)
        save_keywords_to_db(user_id, brand, url, language, dateRange, keywords_df)

        return {
            "success": True,
            "message": "Keywords extracted and saved successfully!",
            "keywords": keywords_df["Keyword"].tolist()
        }

    except Exception as e:
        print("❌ Error in Sinhala pipeline:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Keyword Extraction Failed: {str(e)}")


# ✅ Scoring based on JSON files
def score_and_rank_keywords(folder_path):
    json_files = {
        "KeyBERT": os.path.join(folder_path, "KeyBERT_keywords.json"),
        "Financial": os.path.join(folder_path, "sinhala_financial_vocab.json")
    }

    score_map = {
        "KeyBERT": 3,
        "Financial": 4
    }

    keyword_scores = defaultdict(int)

    for method, file_path in json_files.items():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                keyword_data = json.load(f)

            if isinstance(keyword_data, dict):
                keyword_data = [keyword_data]

            for item in keyword_data:
                if isinstance(item, dict) and "keywords" in item:
                    keywords = item["keywords"]
                    if isinstance(keywords, str):
                        keywords = json.loads(keywords)
                    for keyword in keywords:
                        keyword_scores[keyword] += score_map[method]
                elif isinstance(keyword_data, list) and isinstance(item, str):
                    keyword_scores[item] += score_map[method]

        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except json.JSONDecodeError:
            print(f"❌ JSON decode error in {file_path}")

    sorted_keywords = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)
    return pd.DataFrame(sorted_keywords, columns=["Keyword", "Score"])


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
