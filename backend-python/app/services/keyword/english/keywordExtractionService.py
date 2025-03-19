import os
import json
import pandas as pd
import spacy
import ast
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

# ✅ Load environment variables
load_dotenv()

# ✅ MongoDB Configuration
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = "keywords"

# ✅ Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

DATA_DIR = "data"
CLEANED_SCRAPED_FILE = os.path.join(DATA_DIR, "cleaned_scraped_content.json")
HYBRID_KEYWORDS_FILE = os.path.join(DATA_DIR, "hybrid_keywords.csv")
FINAL_KEYWORDS_FILE = os.path.join(DATA_DIR, "final_keywords.json")  # ✅ New file to store filtered financial keywords

# ✅ Load NLP model
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))

# ✅ Load Financial Vocabulary List (Case-Insensitive Matching)
FINANCIAL_VOCAB_FILE = os.path.join(DATA_DIR, "new_financial_vocabulary.json")
if os.path.exists(FINANCIAL_VOCAB_FILE):
    with open(FINANCIAL_VOCAB_FILE, "r", encoding="utf-8") as f:
        financial_vocab = set(word.lower().strip() for word in json.load(f))
else:
    financial_vocab = set()
    print("⚠️ Financial vocabulary file not found! Ensure `new_financial_vocabulary.json` exists.")


async def process_full_extraction(user_id, brand, url, dateRange, language):
    """
    Full pipeline: Scrape → Preprocess → Extract Keywords → Score & Filter Financial Keywords → Save to DB.
    """
    try:
        # ✅ Step 1: Scrape Content
        scrape_result = await scrape_content(url, dateRange)
        if not scrape_result or "scraped_content" not in scrape_result:
            raise HTTPException(status_code=500, detail="Scraping failed. No content returned.")

        preprocess_success = await preprocess_content()
        if not preprocess_success:
            raise HTTPException(status_code=500, detail="Preprocessing failed. No processed content.")

        if not os.path.exists(CLEANED_SCRAPED_FILE):
            raise HTTPException(status_code=500, detail="Preprocessed content file not found.")

        with open(CLEANED_SCRAPED_FILE, "r", encoding="utf-8") as f:
            cleaned_content = json.load(f)
            if not isinstance(cleaned_content, list) or not cleaned_content:
                raise ValueError("Invalid JSON format. Expected a list of sentences.")

        # ✅ Step 4: Extract Keywords
        await ner_extraction()
        await yake_extraction()
        await keybert_extraction()
        await embedrank_extraction()

        # ✅ Step 5: Score, Rank, and Filter Financial Keywords
        extracted_keywords = score_and_rank_keywords()
        if extracted_keywords.empty:
            print("⚠️ No keywords found.")
            return {"message": "No keywords extracted."}

        financial_keywords = filter_financial_keywords(extracted_keywords)

        # ✅ Fix: Use `.empty` to check if DataFrame is empty
        if financial_keywords.empty:
            print("⚠️ No financial keywords found.")
            return {"message": "No relevant financial keywords extracted."}

        # ✅ Step 6: Save to `final_keywords.json`
        save_final_keywords(user_id, brand, url, language, financial_keywords)

        # ✅ Step 7: Save to MongoDB
        save_keywords_to_db(user_id, brand, url, financial_keywords)

        print("✅ Full extraction process completed successfully!")
        return {"success": True, "message": "Financial Keywords extracted and saved successfully!"}

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error in process_full_extraction:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Keyword Extraction Failed: {str(e)}")


# ✅ Function: Clean Keywords (Fix for 'clean_keywords' not defined)
def clean_keywords(keyword_list):
    """
    Cleans a list of keywords by:
    - Removing duplicates
    - Converting to lowercase
    - Stripping leading/trailing spaces
    """
    if not keyword_list:
        return set()
    
    return set(kw.strip().lower() for kw in keyword_list if isinstance(kw, str) and kw.strip())


# ✅ Function: Score Keywords
def score_keywords(row):
    try:
        yake_keywords = clean_keywords(set(ast.literal_eval(row.get("yake_keywords", "[]"))))
        keybert_keywords = clean_keywords(set(ast.literal_eval(row.get("keybert_keyphrases", "[]"))))
        embedrank_keywords = clean_keywords(set(ast.literal_eval(row.get("embedrank_keywords", "[]"))))

        all_keywords = yake_keywords | keybert_keywords | embedrank_keywords

        keyword_scores = {}
        for kw in all_keywords:
            score = 0
            if kw in yake_keywords:
                score += 3
            if kw in keybert_keywords:
                score += 2
            if kw in embedrank_keywords:
                score += 4
            keyword_scores[kw] = score

        return keyword_scores
    except Exception as e:
        print(f"⚠️ Error scoring keywords: {e}")
        return {}


# ✅ Function: Score & Rank Keywords
def score_and_rank_keywords():
    df_keywords_sorted = pd.DataFrame(columns=["Keyword", "Score"])
    
    if os.path.exists(HYBRID_KEYWORDS_FILE):
        df = pd.read_csv(HYBRID_KEYWORDS_FILE)
        df["scored_keywords"] = df.apply(score_keywords, axis=1)

        keyword_scores_global = {}
        for row in df["scored_keywords"]:
            if isinstance(row, dict):
                for kw, score in row.items():
                    keyword_scores_global[kw] = keyword_scores_global.get(kw, 0) + score

        df_keywords_sorted = pd.DataFrame(list(keyword_scores_global.items()), columns=["Keyword", "Score"])
        df_keywords_sorted = df_keywords_sorted.sort_values(by="Score", ascending=False)

    return df_keywords_sorted


# ✅ Function: Filter Financial Keywords
def filter_financial_keywords(df):
    """
    Filters keywords that exist in the financial vocabulary list.
    Ensures case-insensitive matching for accuracy.
    """
    df["Keyword"] = df["Keyword"].astype(str).str.lower().str.strip()
    return df[df["Keyword"].isin(financial_vocab)]



# ✅ Function: Save Final Filtered Keywords to `final_keywords.json`
def save_final_keywords(user_id, brand, url, language, keywords):
    final_data = {
        "user_id": user_id,
        "brand": brand,
        "url": url,
        "language": language,
        "KeywordList": keywords["Keyword"].tolist(),
    }

    with open(FINAL_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Final financial keywords saved to {FINAL_KEYWORDS_FILE}")


# ✅ Function: Save Extracted Keywords to MongoDB
def save_keywords_to_db(user_id, brand, url, extracted_keywords):
    try:
        keyword_list = extracted_keywords["Keyword"].tolist()

        # ✅ Store extracted keywords in MongoDB
        collection.update_one(
            {"user_id": user_id, "brand": brand, "url": url},
            {"$set": {"KeywordList": keyword_list}},
            upsert=True
        )

        print("✅ Financial Keywords saved to MongoDB successfully!")

    except Exception as e:
        print(f"❌ MongoDB save failed: {e}")
        raise HTTPException(status_code=500, detail=f"MongoDB Save Failed: {str(e)}")
