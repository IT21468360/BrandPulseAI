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

DATA_DIR = os.path.join("data", "keyword", "english")
FINAL_KEYWORDS_FILE = os.path.join(DATA_DIR, "final_boosted_keywords.json")

# ✅ Load NLP model
nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))

# ✅ Load Financial Vocabulary List
FINANCIAL_VOCAB_FILE = os.path.join(DATA_DIR, "new_financial_vocabulary.json")
if os.path.exists(FINANCIAL_VOCAB_FILE):
    with open(FINANCIAL_VOCAB_FILE, "r", encoding="utf-8") as f:
        financial_vocab = set(word.lower().strip() for word in json.load(f))
else:
    financial_vocab = set()
    print("⚠️ Financial vocabulary file not found! Ensure `new_financial_vocabulary.json` exists.")

# ✅ Main pipeline function
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

        # Step 4: Score & Combine
        keywords_df = score_and_rank_keywords()
        if keywords_df.empty:
            status_messages.append("⚠️ No keywords extracted.")
            return {
                "success": False,
                "message": "No keywords extracted.",
                "keywords": [],
                "statusMessages": status_messages
            }
        status_messages.append("📊 Keyword scoring done")

        # Step 5: Boost financial terms
        boosted_df = boost_financial_keywords(keywords_df)
        status_messages.append("💸 Financial boost scoring applied")

        # Step 6: Filter by financial vocab
        filtered_df = boosted_df[boosted_df["Keyword"].isin(financial_vocab)]
        if filtered_df.empty:
            status_messages.append("⚠️ No matches in financial vocabulary")
            return {
                "success": False,
                "message": "No financial matches found",
                "keywords": [],
                "statusMessages": status_messages
            }

        # Step 7: Save to DB & JSON
        save_final_keywords(user_id, brand, url, language, dateRange, filtered_df)
        save_keywords_to_db(user_id, brand, url, language, dateRange, filtered_df)
        status_messages.append("💾 Saved to database")

        status_messages.append("✅ Keyword extraction complete")

        return {
            "success": True,
            "message": "Financial Keywords extracted and saved successfully!",
            "keywords": boosted_df["Keyword"].astype(str).tolist(),
            "statusMessages": status_messages
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


# ✅ Combine & Score Keywords
def score_and_rank_keywords():
    folder_path = DATA_DIR
    try:
        with open(f"{folder_path}/unique_yake_keywords.json", "r", encoding="utf-8") as f:
            yake_keywords = set(kw.lower().strip() for kw in json.load(f))

        with open(f"{folder_path}/unique_keybert_keyphrases.json", "r", encoding="utf-8") as f:
            keybert_keywords = set(kw.lower().strip() for kw in json.load(f))

        with open(f"{folder_path}/unique_embedrank_keyphrases.json", "r", encoding="utf-8") as f:
            embedrank_keywords = set(kw.lower().strip() for kw in json.load(f))

        with open(f"{folder_path}/unique_ner_words.json", "r", encoding="utf-8") as f:
            ner_keywords = set(kw.lower().strip() for kw in json.load(f))

        with open(f"{folder_path}/unique_ner_word_tag_pairs.json", "r", encoding="utf-8") as f:
            ner_word_tag_pairs_raw = json.load(f)

        ner_word_tag_dict = {kw.lower(): tag for kw, tag in ner_word_tag_pairs_raw}

        all_keywords = yake_keywords | keybert_keywords | embedrank_keywords | ner_keywords

        scored_data = []
        for kw in all_keywords:
            score = 0
            if kw in yake_keywords:
                score += 2
            if kw in keybert_keywords:
                score += 3
            if kw in embedrank_keywords:
                score += 4
            if kw in ner_keywords:
                score += 5

            entity = ner_word_tag_dict.get(kw, "")
            scored_data.append({"Keyword": kw, "Score": score, "NER_Entity": entity})

        df_keywords = pd.DataFrame(scored_data)
        df_keywords = df_keywords.sort_values(by="Score", ascending=False)

        return df_keywords

    except Exception as e:
        print(f"❌ Failed to score keywords: {e}")
        return pd.DataFrame()


# ✅ Boost scores for financial keywords
def boost_financial_keywords(df):
    try:
        df["Boosted_Score"] = df.apply(lambda row: row["Score"] * 1.5 if row["Keyword"] in financial_vocab else row["Score"], axis=1)
        df = df.sort_values(by="Boosted_Score", ascending=False)
        return df
    except Exception as e:
        print(f"❌ Failed to boost scores: {e}")
        return pd.DataFrame()


# ✅ Save to JSON
def save_final_keywords(user_id, brand, url, language, dateRange, keywords_df):
    final_data = {
        "user_id": user_id,
        "brand": brand,
        "url": url,
        "language": language,
        "KeywordList": keywords_df["Keyword"].tolist(),
    }

    with open(FINAL_KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Final financial keywords saved to {FINAL_KEYWORDS_FILE}")
