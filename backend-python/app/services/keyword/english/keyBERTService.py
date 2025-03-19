import os
import json
import pandas as pd
from fastapi import APIRouter, HTTPException
from keybert import KeyBERT
from transformers import AutoTokenizer, AutoModel

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths for input/output files
CLEANED_SCRAPED_FILE = os.path.join("data", "cleaned_scraped_content.json")
KEYBERT_KEYPHRASES_FILE_JSON = os.path.join("data", "keybert_finbert_keyphrases.json")
KEYBERT_KEYPHRASES_FILE_CSV = os.path.join("data", "keybert_finbert_keyphrases.csv")

# ✅ Ensure `data` directory exists
os.makedirs("data", exist_ok=True)

FINBERT_MODEL_PATH = "./app/models/finbertKeywordExtraction"

# ✅ Ensure the directory exists
if not os.path.isdir(FINBERT_MODEL_PATH):
    raise RuntimeError(f"❌ Model directory not found: {FINBERT_MODEL_PATH}")

try:
    finbert_model = AutoModel.from_pretrained(FINBERT_MODEL_PATH, local_files_only=True, ignore_mismatched_sizes=True)
    finbert_tokenizer = AutoTokenizer.from_pretrained(FINBERT_MODEL_PATH, local_files_only=True, ignore_mismatched_sizes=True)
    print("✅ Successfully loaded fine-tuned FinBERT model from local directory!")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load fine-tuned FinBERT model: {e}")

# ✅ Initialize KeyBERT with Fine-Tuned FinBERT
kw_model = KeyBERT(model=finbert_model)

def extract_keyphrases_keybert(text, top_n=5):
    """
    Extracts keyphrases using KeyBERT with the fine-tuned FinBERT model.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    keyphrases = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=top_n,
        use_mmr=True,
        diversity=0.7
    )

    return [kp[0] for kp in keyphrases]

async def keybert_extraction():
    """
    Loads cleaned sentences, extracts keyphrases using KeyBERT + FinBERT, and saves results.
    """
    try:
        if not os.path.exists(CLEANED_SCRAPED_FILE):
            print("❌ KeyBERT ERROR: Preprocessed content file not found.")
            raise HTTPException(status_code=404, detail="Preprocessed content file not found.")

        with open(CLEANED_SCRAPED_FILE, "r", encoding="utf-8") as f:
            cleaned_content = json.load(f)

        if not cleaned_content:
            print("❌ KeyBERT ERROR: Cleaned content is empty.")
            raise HTTPException(status_code=500, detail="No valid content for KeyBERT keyword extraction.")

        df = pd.DataFrame(cleaned_content, columns=["Sentence"])

        df["keybert_keyphrases"] = df["Sentence"].apply(extract_keyphrases_keybert)

        df.to_csv(KEYBERT_KEYPHRASES_FILE_CSV, index=False, encoding="utf-8")

        print("✅ KeyBERT extraction completed successfully!")
        return {"success": True, "message": "KeyBERT + FinBERT extraction completed!"}

    except Exception as e:
        print(f"❌ KeyBERT extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
