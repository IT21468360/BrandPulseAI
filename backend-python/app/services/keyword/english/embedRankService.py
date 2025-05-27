import os
import json
import pandas as pd
import ast
import time
from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer, util

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths
DATA_DIR = os.path.join("data", "keyword", "english")
PARAGRAPH_FILE = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
YAKE_FILE = os.path.join(DATA_DIR, "yake_keywords_per_sentence.csv")
KEYBERT_FILE = os.path.join(DATA_DIR, "keybert_keywords_per_paragraph.csv")
EMBEDRANK_OUTPUT_CSV = os.path.join(DATA_DIR, "embedrank_keywords.csv")
UNIQUE_EMBEDRANK_JSON = os.path.join(DATA_DIR, "unique_embedrank_keyphrases.json")
EMBEDRANK_FINANCIAL_JSON = os.path.join(DATA_DIR, "embedrank_financial_keyphrases.json")
FINANCIAL_VOCAB_FILE = os.path.join(DATA_DIR, "new_financial_vocabulary.json")

# ✅ Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Load Financial Vocabulary
try:
    with open(FINANCIAL_VOCAB_FILE, "r", encoding="utf-8") as f:
        financial_vocab = set(word.lower().strip() for word in json.load(f))
except Exception as e:
    raise RuntimeError(f"❌ Failed to load financial vocabulary: {e}")

# ✅ Load Sentence Transformer
embed_model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-v3")

# ✅ Noise filter
NOISE_WORDS = {
    "news", "latest", "update", "updates", "cookies", "best", "website",
    "experience", "tags", "awards", "day", "month", "plc", "csr"
}

def is_valid_phrase(phrase, min_len=2):
    phrase = phrase.strip().lower()
    if len(phrase.split()) < min_len:
        return False
    return not any(noise in phrase for noise in NOISE_WORDS)

# ✅ EmbedRank core logic
def extract_embedrank_keywords(text, yake_keywords, keybert_keywords, top_n=5):
    start_time = time.time()

    yake_keywords = yake_keywords if isinstance(yake_keywords, list) else []
    keybert_keywords = keybert_keywords if isinstance(keybert_keywords, list) else []
    keywords = list(set(yake_keywords + keybert_keywords))
    if not keywords:
        return [], 0.0

    text_embedding = embed_model.encode(text, convert_to_tensor=True)
    word_embeddings = embed_model.encode(keywords, convert_to_tensor=True)
    similarity_scores = util.pytorch_cos_sim(text_embedding, word_embeddings)[0]

    ranked = sorted(zip(keywords, similarity_scores.tolist()), key=lambda x: x[1], reverse=True)
    filtered = [kw for kw, score in ranked if is_valid_phrase(kw)]

    end_time = time.time()
    return filtered[:top_n], (end_time - start_time)

# ✅ Main Route
@router.post("/embedrank-extract")
async def embedrank_extraction():
    """
    Extract keyphrases using EmbedRank and filter for financial vocabulary matches.
    """
    try:
        # ✅ Load input files
        if not all(os.path.exists(p) for p in [PARAGRAPH_FILE, YAKE_FILE, KEYBERT_FILE]):
            raise HTTPException(status_code=404, detail="One or more required files are missing.")

        df_para = pd.read_csv(PARAGRAPH_FILE)
        df_yake = pd.read_csv(YAKE_FILE)
        df_keybert = pd.read_csv(KEYBERT_FILE)

        if "Paragraph" not in df_para.columns:
            raise HTTPException(status_code=500, detail="'Paragraph' column missing.")

        # ✅ Parse YAKE + KeyBERT keyword lists
        df_yake["yake_keywords"] = df_yake["yake_keywords"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        df_keybert["keybert_keyphrases"] = df_keybert["keybert_keyphrases"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

        # ✅ Merge
        df = df_para.merge(df_yake, on="Paragraph", how="left").merge(df_keybert, on="Paragraph", how="left")

        # ✅ Apply EmbedRank
        df["embedrank_keywords"], df["embedrank_time"] = zip(*df.apply(
            lambda row: extract_embedrank_keywords(row["Paragraph"], row["yake_keywords"], row["keybert_keyphrases"]),
            axis=1
        ))

        # ✅ Save CSV
        df.to_csv(EMBEDRANK_OUTPUT_CSV, index=False, encoding="utf-8")

        # ✅ Extract all unique keywords
        all_keywords = [
            kw.lower().strip()
            for phrases in df["embedrank_keywords"]
            if isinstance(phrases, list)
            for kw in phrases
        ]
        unique_keywords = sorted(set(all_keywords))

        with open(UNIQUE_EMBEDRANK_JSON, "w", encoding="utf-8") as f:
            json.dump(unique_keywords, f, indent=4, ensure_ascii=False)

        # ✅ Match with financial vocabulary
        matched_keywords = [kw for kw in unique_keywords if kw in financial_vocab]

        with open(EMBEDRANK_FINANCIAL_JSON, "w", encoding="utf-8") as f:
            json.dump(matched_keywords, f, indent=4, ensure_ascii=False)

        print("\n🔟 Sample Financial Matches (EmbedRank):")
        for kw in matched_keywords[:10]:
            print(f"- {kw}")

        return {
            "success": True,
            "message": "✅ EmbedRank extraction and financial keyword filtering completed.",
            "embedrank_csv_file": EMBEDRANK_OUTPUT_CSV,
            "unique_embedrank_json_file": UNIQUE_EMBEDRANK_JSON,
            "embedrank_financial_json_file": EMBEDRANK_FINANCIAL_JSON
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ EmbedRank extraction failed: {e}")
