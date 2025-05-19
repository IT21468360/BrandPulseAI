import os
import json
import spacy
import subprocess
import pandas as pd
import ast
from fastapi import APIRouter, HTTPException

# Initialize FastAPI Router
router = APIRouter()

# Paths
DATA_DIR = os.path.join("data", "keyword", "english")
CLEANED_PARAGRAPH_CSV = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
NER_EXTRACTED_FILE_JSON = os.path.join(DATA_DIR, "ner_extracted_sentences.json")
UNIQUE_WORDS_FILE = os.path.join(DATA_DIR, "unique_ner_words.json")
UNIQUE_PAIRS_FILE = os.path.join(DATA_DIR, "unique_ner_word_tag_pairs.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load Fine-Tuned SpaCy NER Model
try:
    nlp = spacy.load("en_finetuned_spacy_ner")
    print("✅ SpaCy NER model loaded from environment.")
except OSError:
    print("⚠️ SpaCy NER model not found. Installing from Hugging Face...")
    subprocess.run([
        "pip", "install",
        "https://huggingface.co/Azmarah/finetuned-spacy-ner/resolve/main/en_finetuned_spacy_ner-1.0.0-py3-none-any.whl"
    ], check=True)
    nlp = spacy.load("en_finetuned_spacy_ner")
    print("✅ SpaCy NER model installed and loaded.")

def extract_ner_tags(sentence):
    """Extracts NER tags using the fine-tuned SpaCy model"""
    doc = nlp(sentence)
    return [[ent.text, ent.label_, ent.start_char, ent.end_char] for ent in doc.ents]

# @router.post("/ner-extract")
async def ner_extraction():
    """
    Extract NER tags from cleaned paragraphs, save results,
    and generate unique NER words and word-tag pairs.
    """
    try:
        # ✅ Load cleaned CSV file
        if not os.path.exists(CLEANED_PARAGRAPH_CSV):
            raise HTTPException(status_code=404, detail="❌ Cleaned paragraph file not found.")

        df = pd.read_csv(CLEANED_PARAGRAPH_CSV)

        if "Paragraph" not in df.columns:
            raise HTTPException(status_code=500, detail="❌ 'Paragraph' column missing in CSV.")

        if df.empty:
            raise HTTPException(status_code=500, detail="❌ DataFrame is empty.")

        # ✅ Apply NER extraction
        df["entities"] = df["Paragraph"].apply(extract_ner_tags)

        # ✅ Save full results
        with open(NER_EXTRACTED_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4, ensure_ascii=False)

        # ✅ Extract unique words and (word, tag) pairs
        words_only = set()
        word_tag_pairs = set()

        for tags in df["entities"]:
            for tag in tags:
                if isinstance(tag, list) and len(tag) >= 2:
                    word = str(tag[0]).strip()
                    label = str(tag[1]).strip()
                    words_only.add(word)
                    word_tag_pairs.add((word, label))

        unique_words = sorted(words_only)
        unique_word_tag_pairs = sorted(word_tag_pairs)

        # ✅ Save to JSON
        with open(UNIQUE_WORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_words, f, indent=4, ensure_ascii=False)

        with open(UNIQUE_PAIRS_FILE, "w", encoding="utf-8") as f:
            json.dump(unique_word_tag_pairs, f, indent=4, ensure_ascii=False)

        return {
            "success": True,
            "message": "✅ NER extraction and unique term generation completed.",
            "ner_json_file": NER_EXTRACTED_FILE_JSON,
            "unique_words_file": UNIQUE_WORDS_FILE,
            "unique_pairs_file": UNIQUE_PAIRS_FILE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ NER extraction failed: {e}")
