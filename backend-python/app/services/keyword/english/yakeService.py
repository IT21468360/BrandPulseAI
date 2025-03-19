import os
import json
import pandas as pd
import yake
from fastapi import APIRouter, HTTPException

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths for input/output files
CLEANED_SCRAPED_FILE = os.path.join("data", "cleaned_scraped_content.json")
YAKE_KEYWORDS_FILE_JSON = os.path.join("data", "yake_keywords.json")
YAKE_KEYWORDS_FILE_CSV = os.path.join("data", "yake_keywords.csv")

# ✅ Ensure `data` directory exists
os.makedirs("data", exist_ok=True)

# ✅ Initialize YAKE Keyword Extractor
yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=10, features=None)

def extract_keywords_yake(text):
    """
    Extracts keywords using YAKE algorithm.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    
    keywords = yake_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]  # Extract just the keyword strings

@router.post("/yake-extract")
async def yake_extraction():
    """
    Loads cleaned sentences, extracts keywords using YAKE, and saves results.
    """
    try:
        if not os.path.exists(CLEANED_SCRAPED_FILE):
            print("❌ YAKE ERROR: Preprocessed content file not found.")
            raise HTTPException(status_code=404, detail="Preprocessed content file not found.")

        with open(CLEANED_SCRAPED_FILE, "r", encoding="utf-8") as f:
            cleaned_content = json.load(f)

        if not cleaned_content:
            print("❌ YAKE ERROR: Cleaned content is empty.")
            raise HTTPException(status_code=500, detail="No valid content for YAKE keyword extraction.")

        # ✅ Convert JSON to DataFrame
        df = pd.DataFrame(cleaned_content, columns=["Sentence"])

        # ✅ Extract Keywords
        df["yake_keywords"] = df["Sentence"].apply(extract_keywords_yake)

        # ✅ Save results to JSON file
        with open(YAKE_KEYWORDS_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4, ensure_ascii=False)

        # ✅ Save results to CSV file
        df.to_csv(YAKE_KEYWORDS_FILE_CSV, index=False, encoding="utf-8")

        print("✅ YAKE extraction completed successfully!")
        return {
            "success": True,
            "message": "YAKE keyword extraction completed successfully!",
            "yake_json_file": YAKE_KEYWORDS_FILE_JSON,
            "yake_csv_file": YAKE_KEYWORDS_FILE_CSV
        }

    except Exception as e:
        print(f"❌ YAKE extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
