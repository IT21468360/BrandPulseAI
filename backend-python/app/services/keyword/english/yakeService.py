import os
import json
import pandas as pd
import yake
import time
from fastapi import APIRouter, HTTPException

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths for input/output files
DATA_DIR = os.path.join("data", "keyword", "english")
CLEANED_SCRAPED_FILE = os.path.join(DATA_DIR, "cleaned_scraped_paragraphs.json")
YAKE_KEYWORDS_FILE_JSON = os.path.join(DATA_DIR, "yake_keywords.json")
YAKE_KEYWORDS_FILE_CSV = os.path.join(DATA_DIR, "yake_keywords_per_sentence.csv")
UNIQUE_YAKE_KEYWORDS_FILE = os.path.join(DATA_DIR, "unique_yake_keywords.json")

# ✅ Ensure `data` directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Initialize YAKE Keyword Extractor
yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=10, features=None)

def extract_keywords_yake(text):
    """
    Extracts keywords using YAKE while measuring execution time.
    """
    start_time = time.time()
    keywords = yake_extractor.extract_keywords(text)
    extracted_keywords = [kw[0] for kw in keywords]
    end_time = time.time()
    return extracted_keywords, (end_time - start_time)

@router.post("/yake-extract")
async def yake_extraction():
    """
    Loads cleaned paragraphs, extracts keywords using YAKE,
    and saves keywords, execution times, and unique terms.
    """
    try:
        if not os.path.exists(CLEANED_SCRAPED_FILE):
            raise HTTPException(status_code=404, detail="Preprocessed content file not found.")

        with open(CLEANED_SCRAPED_FILE, "r", encoding="utf-8") as f:
            cleaned_content = json.load(f)

        if not cleaned_content:
            raise HTTPException(status_code=500, detail="Cleaned content is empty.")

        # ✅ Convert JSON to DataFrame
        df = pd.DataFrame(cleaned_content, columns=["Paragraph"])

        # ✅ Apply YAKE
        df["yake_keywords"], df["yake_execution_time"] = zip(*df["Paragraph"].apply(extract_keywords_yake))

        # ✅ Save results to CSV
        df.to_csv(YAKE_KEYWORDS_FILE_CSV, index=False, encoding="utf-8")

        # ✅ Save full results to JSON
        with open(YAKE_KEYWORDS_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4, ensure_ascii=False)

        # ✅ Flatten and save unique keywords
        all_yake_keywords = [kw.lower().strip() for keywords in df["yake_keywords"] for kw in keywords]
        unique_keywords = sorted(set(all_yake_keywords))

        with open(UNIQUE_YAKE_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_keywords, f, indent=4, ensure_ascii=False)

        # 🖨️ Sample output
        print("\n🔟 Sample Unique YAKE Keywords:")
        for kw in unique_keywords[:10]:
            print(f"- {kw}")

        return {
            "success": True,
            "message": "✅ YAKE keyword extraction and unique list generation completed.",
            "yake_csv_file": YAKE_KEYWORDS_FILE_CSV,
            "yake_json_file": YAKE_KEYWORDS_FILE_JSON,
            "unique_yake_keywords_file": UNIQUE_YAKE_KEYWORDS_FILE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ YAKE extraction failed: {e}")
