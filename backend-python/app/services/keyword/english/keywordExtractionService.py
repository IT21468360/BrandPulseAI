import os
import json
import pandas as pd
import spacy
from nltk.corpus import stopwords
from fastapi import HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
from app.services.keyword.english.scraperService import scrape_content
from app.services.keyword.english.preprocessService import preprocess_content
from app.services.keyword.english.databaseService import save_keywords_to_db
from app.services.keyword.english.yakeService import yake_extraction
from app.services.keyword.english.keyBERTService import keybert_extraction
from app.services.keyword.english.embedRankService import embedrank_extraction
from app.services.keyword.english.nerService import ner_extraction
import traceback

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "keywords"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

DATA_DIR = os.path.join("data", "keyword", "english")
FINAL_KEYWORDS_FILE = os.path.join(DATA_DIR, "final_boosted_keywords.json")

# Load NLP model
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))

# Load Financial Vocabulary List
FINANCIAL_VOCAB_FILE = os.path.join(DATA_DIR, "new_financial_vocabulary.json")
if os.path.exists(FINANCIAL_VOCAB_FILE):
    with open(FINANCIAL_VOCAB_FILE, "r", encoding="utf-8") as f:
        financial_vocab = set(word.lower().strip() for word in json.load(f))
else:
    financial_vocab = set()
    print("⚠️ Financial vocabulary file not found! Ensure `new_financial_vocabulary.json` exists.")

# Main pipeline function
async def process_full_extraction(user_id, brand, url, dateRange, language):
    try:
        status_messages = []

        # Step 1: Scraping
        scrape_result = await scrape_content(url, dateRange)
        if not scrape_result or "scraped_content" not in scrape_result:
            raise HTTPException(status_code=500, detail="Scraping failed.")
        status_messages.append("🔍 Scraping completed")

        # Step 2: Preprocessing
        if not await preprocess_content():
            raise HTTPException(status_code=500, detail="Preprocessing failed.")
        status_messages.append("🧹 Preprocessing completed")

        # Step 3: Keyword Extraction (NER, YAKE, KeyBERT, EmbedRank)
        await ner_extraction()
        status_messages.append("🧠 NER extraction done")

        await yake_extraction()
        status_messages.append("🔍 YAKE extraction done")

        await keybert_extraction()
        status_messages.append("🧠 KeyBERT extraction done")

        await embedrank_extraction()
        status_messages.append("🔗 EmbedRank completed")

        # Step 4: Merge financial keywords from all validated files
        financial_keyword_files = [
            "yake_financial_keywords.json",
            "keybert_financial_keyphrases.json",
            "embedrank_financial_keyphrases.json",
            "ner_financial_words.json"
        ]
        all_financial_keywords = set()
        for file in financial_keyword_files:
            path = os.path.join(DATA_DIR, file)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    kws = json.load(f)
                    all_financial_keywords.update(kw.lower().strip() for kw in kws if isinstance(kw, str))

        final_keywords = sorted(all_financial_keywords)
        if not final_keywords:
            status_messages.append("⚠️ No financial keywords found after merge.")
            return {
                "success": False,
                "message": "No financial keywords found.",
                "keywords": [],
                "statusMessages": status_messages
            }

        # Step 5: Save to JSON and MongoDB
        final_data = {
            "user_id": user_id,
            "brand": brand,
            "url": url,
            "language": language,
            "KeywordList": final_keywords
        }
        with open(FINAL_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Final financial keywords saved to {FINAL_KEYWORDS_FILE}")

        merged_doc = {
            "user_id": user_id,
            "brand": brand,
            "url": url,
            "language": language,
            "date_range": dateRange,
            "financial_keywords": final_keywords,
            "source": "Merged_YAKE_KeyBERT_EmbedRank_NER",
            "timestamp": pd.Timestamp.now().isoformat()
        }
        collection.insert_one(merged_doc)
        status_messages.append("📥 Final unique financial keywords saved to MongoDB")

        status_messages.append("✅ Keyword extraction complete")

        return {
            "success": True,
            "message": "Financial Keywords extracted and saved successfully!",
            "keywords": final_keywords,
            "statusMessages": status_messages
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
