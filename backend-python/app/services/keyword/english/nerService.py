import os
import json
import spacy
import subprocess
import pandas as pd
from fastapi import APIRouter, HTTPException

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ File Paths
DATA_DIR = os.path.join("data", "keyword", "english")
CLEANED_PARAGRAPH_CSV = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
NER_EXTRACTED_FILE_JSON = os.path.join(DATA_DIR, "ner_extracted_sentences.json")
UNIQUE_WORDS_FILE = os.path.join(DATA_DIR, "unique_ner_words.json")
UNIQUE_PAIRS_FILE = os.path.join(DATA_DIR, "unique_ner_word_tag_pairs.json")
NER_FINANCIAL_WORDS_FILE = os.path.join(DATA_DIR, "ner_financial_words.json")
FINANCIAL_VOCAB_FILE = os.path.join(DATA_DIR, "new_financial_vocabulary.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Load Financial Vocabulary
try:
    with open(FINANCIAL_VOCAB_FILE, "r", encoding="utf-8") as f:
        financial_vocab = set(word.lower().strip() for word in json.load(f))
except Exception as e:
    raise RuntimeError(f"❌ Failed to load financial vocabulary: {e}")

# ✅ Load Fine-tuned SpaCy NER model
try:
    nlp = spacy.load("en_finetuned_spacy_ner")
    print("✅ SpaCy NER model loaded.")
except OSError:
    print("⚠️ Model not found. Installing...")
    subprocess.run([
        "pip", "install",
        "https://huggingface.co/Azmarah/finetuned-spacy-ner/resolve/main/en_finetuned_spacy_ner-1.0.0-py3-none-any.whl"
    ], check=True)
    nlp = spacy.load("en_finetuned_spacy_ner")
    print("✅ SpaCy NER model installed and loaded.")

# ✅ NER tag extractor
def extract_ner_tags(sentence):
    doc = nlp(sentence)
    return [[ent.text, ent.label_, ent.start_char, ent.end_char] for ent in doc.ents]

# ✅ Main route
@router.post("/ner-extract")
async def ner_extraction():
    """
    Apply NER to cleaned paragraphs, save full tags,
    extract unique entities, and filter financial vocab terms.
    """
    try:
        if not os.path.exists(CLEANED_PARAGRAPH_CSV):
            raise HTTPException(status_code=404, detail="❌ Cleaned paragraph file not found.")

        df = pd.read_csv(CLEANED_PARAGRAPH_CSV)

        if "Paragraph" not in df.columns:
            raise HTTPException(status_code=500, detail="❌ 'Paragraph' column missing.")

        if df.empty:
            raise HTTPException(status_code=500, detail="❌ Paragraph file is empty.")

        # ✅ Apply NER
        df["entities"] = df["Paragraph"].apply(extract_ner_tags)

        # ✅ Save full entity data
        with open(NER_EXTRACTED_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient="records"), f, indent=4, ensure_ascii=False)

        # ✅ Extract unique words and (word, tag) pairs
        unique_words = set()
        unique_word_tag_pairs = set()

        for entity_list in df["entities"]:
            for tag in entity_list:
                if isinstance(tag, list) and len(tag) >= 2:
                    word, label = tag[0].strip(), tag[1].strip()
                    unique_words.add(word)
                    unique_word_tag_pairs.add((word, label))

        sorted_words = sorted(unique_words)
        sorted_pairs = sorted(unique_word_tag_pairs)

        # ✅ Save unique word lists
        with open(UNIQUE_WORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_words, f, indent=4, ensure_ascii=False)

        with open(UNIQUE_PAIRS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_pairs, f, indent=4, ensure_ascii=False)

        # ✅ Filter financial words
        matched_financial_words = sorted([w for w in unique_words if w.lower() in financial_vocab])

        with open(NER_FINANCIAL_WORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(matched_financial_words, f, indent=4, ensure_ascii=False)

        print("\n🔟 Sample Financial Matches from NER:")
        for word in matched_financial_words[:10]:
            print(f"- {word}")

        return {
            "success": True,
            "message": "✅ NER tagging and financial match filtering completed.",
            "ner_json_file": NER_EXTRACTED_FILE_JSON,
            "unique_words_file": UNIQUE_WORDS_FILE,
            "unique_pairs_file": UNIQUE_PAIRS_FILE,
            "ner_financial_words_file": NER_FINANCIAL_WORDS_FILE
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ NER extraction failed: {e}")
