import os
import json
import time
import pandas as pd
from fastapi import APIRouter, HTTPException
from keybert import KeyBERT
from transformers import AutoTokenizer, AutoModel

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths
DATA_DIR = os.path.join("data", "keyword", "english")
CLEANED_PARAGRAPH_FILE = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
KEYBERT_OUTPUT_FILE_CSV = os.path.join(DATA_DIR, "keybert_keywords_per_paragraph.csv")
UNIQUE_KEYBERT_FILE_JSON = os.path.join(DATA_DIR, "unique_keybert_keyphrases.json")

FINBERT_MODEL_PATH = "Azmarah/finbert-keyword-extraction"

# ✅ Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Load fine-tuned FinBERT model

try:
    finbert_model = AutoModel.from_pretrained(FINBERT_MODEL_PATH, ignore_mismatched_sizes=True)
    finbert_tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL_PATH, ignore_mismatched_sizes=True)
    print("✅ Successfully loaded fine-tuned FinBERT model from local directory!")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load fine-tuned FinBERT model: {e}")

# ✅ Initialize KeyBERT
kw_model = KeyBERT(model=finbert_model)

# ✅ Keyphrase extraction function with timing
def extract_keyphrases_keybert(text, top_n=5):
    start_time = time.time()
    try:
        keyphrases = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            top_n=top_n,
            use_mmr=True,
            diversity=0.7
        )
        keyphrases = [kp[0].strip() for kp in keyphrases]
    except Exception as e:
        print(f"❌ Error extracting keyphrases: {e}")
        keyphrases = []
    end_time = time.time()
    return keyphrases, (end_time - start_time)

# ✅ Route: /keybert-extract
@router.post("/keybert-extract")
async def keybert_extraction():
    """
    Extracts keyphrases from cleaned paragraphs using KeyBERT + FinBERT,
    saves results with timing, and stores unique keywords.
    """
    try:
        if not os.path.exists(CLEANED_PARAGRAPH_FILE):
            raise HTTPException(status_code=404, detail="Cleaned paragraph file not found.")

        df = pd.read_csv(CLEANED_PARAGRAPH_FILE)

        if "Paragraph" not in df.columns:
            raise HTTPException(status_code=500, detail="CSV missing 'Paragraph' column.")

        if df.empty:
            raise HTTPException(status_code=500, detail="Paragraph file is empty.")

        # ✅ Apply extraction
        df["keybert_keyphrases"], df["execution_time"] = zip(*df["Paragraph"].apply(extract_keyphrases_keybert))

        # ✅ Save to CSV
        df.to_csv(KEYBERT_OUTPUT_FILE_CSV, index=False, encoding="utf-8")

        # ✅ Flatten and save unique keyphrases
        all_keyphrases = [kw.strip() for keywords in df["keybert_keyphrases"] if isinstance(keywords, list) for kw in keywords]
        unique_keyphrases = sorted(set(all_keyphrases))

        with open(UNIQUE_KEYBERT_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(unique_keyphrases, f, indent=4, ensure_ascii=False)

        print("\n🔟 Sample Unique KeyBERT Keyphrases:")
        for kw in unique_keyphrases[:10]:
            print(f"- {kw}")

        return {
            "success": True,
            "message": "✅ KeyBERT + FinBERT keyphrase extraction completed!",
            "csv_file": KEYBERT_OUTPUT_FILE_CSV,
            "unique_json_file": UNIQUE_KEYBERT_FILE_JSON
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ KeyBERT extraction failed: {e}")
