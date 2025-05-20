import os
import json
import re
import time
import pandas as pd
import torch
import unicodedata
from difflib import SequenceMatcher
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from transformers import AutoTokenizer, AutoModelForTokenClassification

# ✅ FastAPI Router
router = APIRouter()

# ✅ Configuration
DATA_DIR = os.path.join("data", "keyword", "sinhala")
CLEANED_CSV_FILE = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
OUTPUT_JSON_FILE = os.path.join(DATA_DIR, "KeyBERT_keywords.json")

HF_MODEL_NAME = "Azmarah/XLMR-Keyword-Extraction-Sinhala"  # Replace with your model repo

# ✅ Load tokenizer and model
try:
    print("🔄 Loading tokenizer and model...")

    # 🛠 Force load from base model to avoid broken tokenizer.json
    tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base", use_fast=True)

    # 👇 Model still loads from your custom repo
    model = AutoModelForTokenClassification.from_pretrained("Azmarah/XLMR-Keyword-Extraction-Sinhala")
    model.eval()

    print("✅ Model and fallback tokenizer loaded successfully.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load model/tokenizer: {e}")


# ✅ Labels
label_list = ["O", "KEY"]
label_to_id = {label: i for i, label in enumerate(label_list)}
id_to_label = {i: label for label, i in label_to_id.items()}

# ✅ Utility functions
def normalize_sinhala_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)

def fix_sinhala_ligatures(text: str) -> str:
    ligature_map = {
        "ශ්රී": "ශ්‍රී", "ක්ර": "ක්‍ර", "ක්රම": "ක්‍රම", "ප්ර": "ප්‍ර", "ද්ර": "ද්‍ර",
        "ත්ර": "ත්‍ර", "ව්යා": "ව්‍යා", "ව්යාපාර": "ව්‍යාපාර", "ව්යාපාරික": "ව්‍යාපාරික",
        "මධ්යම": "මධ්‍යම"
    }
    for broken, fixed in ligature_map.items():
        text = text.replace(broken, fixed)
    return text

def clean_keyword(kw: str) -> str:
    kw = normalize_sinhala_text(kw)
    kw = fix_sinhala_ligatures(kw)
    kw = re.sub(r"[\u200d\u200c]", "", kw)
    kw = re.sub(r"\s+", " ", kw).strip()
    kw = re.sub(r"^(ය|ඇත්තේ්|අවුරුදු|දරුවන්|අපගේ|අප)\s+", "", kw)
    return kw

def is_valid_keyword(kw: str) -> bool:
    return (
        len(kw) >= 6 and
        len(kw.split()) <= 5 and
        not re.fullmatch(r"[\W_]+", kw) and
        re.search(r"[\u0D80-\u0DFF]", kw) and
        not re.search(r"(අවශ්|ට|ය )$", kw)
    )

def are_similar(a: str, b: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, a, b).ratio() >= threshold

@torch.inference_mode()
def extract_keywords_token_classification(text: str) -> List[str]:
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
        padding="max_length"
    )

    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]
    offset_mapping = encoded["offset_mapping"].squeeze().tolist()
    predictions = torch.argmax(
        model(input_ids=input_ids, attention_mask=attention_mask).logits, dim=2
    ).squeeze().tolist()

    candidate_keywords = []
    current_start, current_end = None, None

    for pred, (start, end) in zip(predictions, offset_mapping):
        if pred == label_to_id["KEY"] and start != end:
            if current_start is None:
                current_start = start
            current_end = end
        else:
            if current_start is not None and current_end is not None:
                keyword = text[current_start:current_end].strip()
                candidate_keywords.append(keyword)
                current_start, current_end = None, None

    if current_start is not None and current_end is not None:
        keyword = text[current_start:current_end].strip()
        candidate_keywords.append(keyword)

    final_keywords = []
    for kw in candidate_keywords:
        kw = clean_keyword(kw)
        if is_valid_keyword(kw) and not any(are_similar(kw, existing) for existing in final_keywords):
            final_keywords.append(kw)

    return final_keywords

# ✅ API Endpoint
@router.post("/sinhala-keyword-extract")
async def keybert_extraction():
    try:
        if not os.path.exists(CLEANED_CSV_FILE):
            raise HTTPException(status_code=404, detail="Cleaned CSV not found.")

        df = pd.read_csv(CLEANED_CSV_FILE)
        if "Paragraph" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV missing 'Paragraph' column.")

        keyword_results = []
        for sentence in df["Paragraph"]:
            keywords = extract_keywords_token_classification(str(sentence))
            keyword_results.append({
                "sentence": sentence,
                "keywords": keywords
            })

        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "message": "✅ Token classification keyword extraction complete.",
            "records": len(keyword_results),
            "output_path": OUTPUT_JSON_FILE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Keyword extraction failed: {e}")


# ✅ Optional: Standalone CLI Execution
def run_keybert_extraction():
    try:
        print("🚀 Starting standalone keyword extraction...")
        if not os.path.exists(CLEANED_CSV_FILE):
            print("❌ Cleaned CSV not found.")
            return False

        df = pd.read_csv(CLEANED_CSV_FILE)
        if "Paragraph" not in df.columns:
            print("❌ CSV missing 'Paragraph' column.")
            return False

        keyword_results = []
        for sentence in df["Paragraph"]:
            keywords = extract_keywords_token_classification(str(sentence))
            keyword_results.append({
                "sentence": sentence,
                "keywords": keywords
            })

        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, ensure_ascii=False, indent=2)

        print(f"✅ Completed! Extracted keywords from {len(df)} records.")
        return True

    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return False

if __name__ == "__main__":
    run_keybert_extraction()
