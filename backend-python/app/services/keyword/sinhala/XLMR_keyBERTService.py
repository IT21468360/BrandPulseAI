import os
import json
import re
import pandas as pd
import torch
import unicodedata
from difflib import SequenceMatcher
from fastapi import APIRouter, HTTPException
from transformers import AutoTokenizer, AutoModelForTokenClassification

# ✅ FastAPI Router
router = APIRouter()

# ✅ Paths
DATA_DIR = os.path.join("data", "keyword", "sinhala")
CLEANED_CSV_FILE = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
OUTPUT_JSON_FILE = os.path.join(DATA_DIR, "KeyBERT_keywords.json")

MODEL_PATH = "C:/Users/Azmarah Rizvi/Desktop/BrandPulseAI/backend-python/app/models/XLMR_Keyword_FineTune/keyword_finetuned_model"

try:
    if not os.path.isdir(MODEL_PATH):
        raise RuntimeError(f"❌ Local model path does not exist: {MODEL_PATH}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    model.eval()

    print("✅ Successfully loaded model and tokenizer from local path.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load model from local directory: {e}")


# ✅ Label setup
label_list = ["O", "KEY"]
label_to_id = {label: i for i, label in enumerate(label_list)}
id_to_label = {i: label for label, i in label_to_id.items()}

# ✅ Utility functions
def are_similar(a, b, threshold=0.85):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def normalize_sinhala_text(text):
    return unicodedata.normalize("NFC", text)

def fix_sinhala_ligatures(text):
    ligature_map = {
        "ශ්රී": "ශ්‍රී", "ක්ර": "ක්‍ර", "ක්රම": "ක්‍රම", "ප්ර": "ප්‍ර", "ද්ර": "ද්‍ර",
        "ත්ර": "ත්‍ර", "ව්යා": "ව්‍යා", "ව්යාපාර": "ව්‍යාපාර", "ව්යාපාරික": "ව්‍යාපාරික",
        "මධ්යම": "මධ්‍යම"
    }
    for broken, fixed in ligature_map.items():
        text = text.replace(broken, fixed)
    return text

def clean_keyword(kw):
    kw = normalize_sinhala_text(kw)
    kw = fix_sinhala_ligatures(kw)
    kw = re.sub(r"[\u200d\u200c]", "", kw)
    kw = re.sub(r"\s+", " ", kw).strip()
    kw = re.sub(r"^(ය|ඇත්තේ්|අවුරුදු|දරුවන්|අපගේ|අප)\s+", "", kw)
    return kw

def is_valid_keyword(kw):
    return (
        len(kw) >= 6 and
        len(kw.split()) <= 5 and
        not re.fullmatch(r"[\W_]+", kw) and
        re.search(r"[\u0D80-\u0DFF]", kw) and
        not re.search(r"(අවශ්|ට|ය )$", kw)
    )

# ✅ Core Keyword Extraction
def extract_keywords_token_classification(text):
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128,
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
        if pred == label_to_id["KEY"] and start is not None and end is not None and end > start:
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

# ✅ FastAPI Endpoint or Async Worker
@router.post("/sinhala-keyword-extract")
async def keybert_extraction():
    try:
        if not os.path.exists(CLEANED_CSV_FILE):
            raise HTTPException(status_code=404, detail="Cleaned CSV not found.")

        df = pd.read_csv(CLEANED_CSV_FILE)

        if "Paragraph" not in df.columns:
            raise HTTPException(status_code=500, detail="CSV missing 'Paragraph' column.")

        keyword_results = []
        for sentence in df["Paragraph"]:
            keywords = extract_keywords_token_classification(sentence)
            keyword_results.append({
                "sentence": sentence,
                "keywords": keywords
            })

        # ✅ Save as JSON
        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, ensure_ascii=False, indent=4)

        print(f"✅ Saved {len(keyword_results)} keyword records to {OUTPUT_JSON_FILE}")

        return {
            "success": True,
            "message": "✅ Token classification keyword extraction complete.",
            "output_file": OUTPUT_JSON_FILE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Sinhala keyword extraction failed: {e}")


def run_keybert_extraction():
    try:
        if not os.path.exists(CLEANED_CSV_FILE):
            print("❌ Cleaned CSV not found.")
            return False

        df = pd.read_csv(CLEANED_CSV_FILE)

        if "Paragraph" not in df.columns:
            print("❌ CSV missing 'Paragraph' column.")
            return False

        keyword_results = []
        for sentence in df["Paragraph"]:
            keywords = extract_keywords_token_classification(sentence)
            keyword_results.append({
                "sentence": sentence,
                "keywords": keywords
            })

        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, ensure_ascii=False, indent=4)

        print(f"✅ Saved {len(keyword_results)} keyword records to {OUTPUT_JSON_FILE}")
        return True

    except Exception as e:
        print(f"❌ Error in run_keybert_extraction: {e}")
        return False
