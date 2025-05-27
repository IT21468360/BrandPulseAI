import os
import json
import time
import pandas as pd
import yake
from fastapi import APIRouter, HTTPException

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths
DATA_DIR = os.path.join("data", "keyword", "english")
CLEANED_SCRAPED_FILE = os.path.join(DATA_DIR, "cleaned_scraped_paragraphs.json")
YAKE_KEYWORDS_FILE_JSON = os.path.join(DATA_DIR, "yake_keywords.json")
YAKE_KEYWORDS_FILE_CSV = os.path.join(DATA_DIR, "yake_keywords_per_sentence.csv")
UNIQUE_YAKE_KEYWORDS_FILE = os.path.join(DATA_DIR, "unique_yake_keywords.json")
FINANCIAL_KEYWORDS_FILE = os.path.join(DATA_DIR, "new_financial_vocabulary.json")
YAKE_FINANCIAL_KEYWORDS_FILE = os.path.join(DATA_DIR, "yake_financial_keywords.json")

# ✅ Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Load financial vocabulary
try:
    with open(FINANCIAL_KEYWORDS_FILE, "r", encoding="utf-8") as f:
        financial_vocab = set(json.load(f))
        financial_vocab = {kw.lower().strip() for kw in financial_vocab}
except Exception as e:
    raise RuntimeError(f"❌ Failed to load financial vocabulary: {e}")

# ✅ Initialize YAKE
yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=10)

# ✅ Keyword extraction
def extract_keywords_yake(text):
    start_time = time.time()
    keywords = yake_extractor.extract_keywords(text)
    extracted_keywords = [kw[0] for kw in keywords]
    end_time = time.time()
    return extracted_keywords, (end_time - start_time)

# ✅ Main route
@router.post("/yake-extract")
async def yake_extraction():
    try:
        if not os.path.exists(CLEANED_SCRAPED_FILE):
            raise HTTPException(status_code=404, detail="Cleaned content not found.")

        with open(CLEANED_SCRAPED_FILE, "r", encoding="utf-8") as f:
            cleaned_content = json.load(f)

        if not cleaned_content:
            raise HTTPException(status_code=500, detail="Cleaned content is empty.")

        # ✅ Convert to DataFrame
        df = pd.DataFrame(cleaned_content, columns=["Paragraph"])

        # ✅ Extract YAKE keywords
        df["yake_keywords"], df["yake_execution_time"] = zip(*df["Paragraph"].apply(extract_keywords_yake))

        # ✅ Save all YAKE keywords per paragraph
        df.to_csv(YAKE_KEYWORDS_FILE_CSV, index=False, encoding="utf-8")

        # ✅ Save paragraph-wise JSON
        with open(YAKE_KEYWORDS_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4, ensure_ascii=False)

        # ✅ Unique keywords
        all_yake_keywords = [
            kw.lower().strip()
            for keywords in df["yake_keywords"]
            for kw in keywords
        ]
        unique_yake_keywords = sorted(set(all_yake_keywords))

        # ✅ Save unique YAKE keywords
        with open(UNIQUE_YAKE_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_yake_keywords, f, indent=4, ensure_ascii=False)

        # ✅ Filter by financial vocabulary
        matched_keywords = [kw for kw in unique_yake_keywords if kw in financial_vocab]

        # ✅ Save financial-matched YAKE keywords
        with open(YAKE_FINANCIAL_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(matched_keywords, f, indent=4, ensure_ascii=False)

        # ✅ Print samples
        print("\n🔟 Sample Financial Vocabulary Matches (YAKE):")
        for kw in matched_keywords[:10]:
            print(f"- {kw}")

        return {
            "success": True,
            "message": "✅ YAKE extraction & financial keyword filtering completed.",
            "yake_csv_file": YAKE_KEYWORDS_FILE_CSV,
            "yake_json_file": YAKE_KEYWORDS_FILE_JSON,
            "unique_yake_keywords_file": UNIQUE_YAKE_KEYWORDS_FILE,
            "matched_financial_keywords_file": YAKE_FINANCIAL_KEYWORDS_FILE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ YAKE extraction failed: {e}")
