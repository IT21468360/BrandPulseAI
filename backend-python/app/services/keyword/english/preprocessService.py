import os
import json
import re
import pandas as pd
from fastapi import HTTPException

# ✅ Define paths for input/output files
DATA_DIR = "data"
RAW_SCRAPED_FILE = os.path.join(DATA_DIR, "raw_scraped_content.json")
CLEANED_SCRAPED_FILE = os.path.join(DATA_DIR, "cleaned_scraped_content.json")
CLEANED_CSV_FILE = os.path.join(DATA_DIR, "cleaned_sentences.csv")

# ✅ Ensure `data` directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Define text cleaning patterns
PATTERNS = {
    "phone": r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
    "url": r'https?://\S+|www\.\S+|\b\S+\.(?:com|org|net|edu|gov|io|lk)\b',
    "question": r'^.*\?$',
    "address": r'\bNo\.?\s\d+[A-Za-z]?[,\s]?.*\b',
    "date": r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{1,2}[a-z]*[,\s]*\d{4}\b',
    "redundant_period": r'(?<=\.)\s*\.(?:\s*\.)*',
    "single_letter": r'\b[a-zA-Z]\b',
    "bullet": r'(?:\u2022|\u25E6|\u2023|\*|-)\s?',
    "all_symbols": r'[^a-zA-Z\s]',
}

# ✅ Function: Preprocess text
def preprocess_text(content_list):
    """
    Cleans the scraped content by removing unwanted patterns.
    """
    if not isinstance(content_list, list):
        raise HTTPException(status_code=400, detail="❌ Preprocessing error: Input data must be a list.")

    cleaned_list = []
    seen_sentences = set()

    for content in content_list:
        try:
            # Ensure string format
            if isinstance(content, dict) and "sentence" in content:
                content = content["sentence"]
            elif not isinstance(content, str):
                continue  # Skip invalid formats

            # Apply regex patterns
            for pattern in PATTERNS.values():
                content = re.sub(pattern, "", content)

            # Normalize spacing
            content = " ".join(content.split())

            # Ensure meaningful sentence length
            words = content.split()
            if len(words) < 5:
                continue

            # Remove duplicates
            if content not in seen_sentences:
                seen_sentences.add(content)
                cleaned_list.append(content)

        except Exception as e:
            print(f"⚠️ Error cleaning content: {e}")

    if not cleaned_list:
        raise HTTPException(status_code=500, detail="❌ No valid content after preprocessing.")

    return cleaned_list


async def preprocess_content():
    """
    Loads scraped content, cleans it, and saves the cleaned version.
    """
    try:
        print("\n🔍 Attempting to load raw scraped content...")  

        # ✅ Load raw content
        if not os.path.exists(RAW_SCRAPED_FILE):
            print("❌ ERROR: Raw scraped content file not found.")
            return False

        with open(RAW_SCRAPED_FILE, "r", encoding="utf-8") as f:
            scraped_content = json.load(f)

        if not isinstance(scraped_content, list) or len(scraped_content) == 0:
            print("❌ ERROR: Raw scraped content is empty or invalid format.")
            return False

        # ✅ Clean the content
        cleaned_content = preprocess_text(scraped_content)
        if not cleaned_content:
            print("❌ ERROR: No valid content after preprocessing.")
            return False

        # ✅ Save cleaned content
        with open(CLEANED_SCRAPED_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_content, f, ensure_ascii=False, indent=2)

        # ✅ Save to CSV
        df = pd.DataFrame(cleaned_content, columns=["Sentence"])
        df.to_csv(CLEANED_CSV_FILE, index=False, encoding="utf-8")

        print(f"✅ Successfully preprocessed {len(cleaned_content)} sentences.")
        return True

    except json.JSONDecodeError:
        print("❌ ERROR: Failed to decode JSON from raw scraped file.")
        return False
    except Exception as e:
        print(f"❌ ERROR in Preprocessing: {e}")
        return False
