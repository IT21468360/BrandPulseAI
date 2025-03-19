import os
import json
import pandas as pd
import ast
from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer, util

# ✅ Initialize FastAPI Router
router = APIRouter()

# ✅ Define paths for input/output files
KEYPHRASE_EXTRACTION_FILE = os.path.join("data", "keybert_finbert_keyphrases.csv")
HYBRID_KEYWORDS_FILE_JSON = os.path.join("data", "hybrid_keywords.json")
HYBRID_KEYWORDS_FILE_CSV = os.path.join("data", "hybrid_keywords.csv")

# ✅ Ensure `data` directory exists
os.makedirs("data", exist_ok=True)

# ✅ Load SentenceTransformer model
embed_model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-v3")

def extract_embedrank_keywords(text, yake_keywords, keybert_keywords, top_n=5):
    """
    Extracts relevant keywords using sentence embeddings (EmbedRank).
    Uses YAKE and KeyBERT keywords, then ranks using semantic similarity.
    """
    keywords = list(set(yake_keywords + keybert_keywords))

    if not keywords:
        return ["No keywords found"]

    text_embedding = embed_model.encode(text, convert_to_tensor=True)
    word_embeddings = embed_model.encode(keywords, convert_to_tensor=True)

    similarity_scores = util.pytorch_cos_sim(text_embedding, word_embeddings)[0]

    ranked_keywords = sorted(zip(keywords, similarity_scores.tolist()), key=lambda x: x[1], reverse=True)[:top_n]

    return [kw[0] for kw in ranked_keywords]

async def embedrank_extraction():
    """
    Loads extracted keyphrases, applies EmbedRank, and saves refined keywords.
    """
    try:
        # ✅ Load extracted keyphrases
        if not os.path.exists(KEYPHRASE_EXTRACTION_FILE):
            raise HTTPException(status_code=404, detail="Keyphrase extraction file not found.")

        df = pd.read_csv(KEYPHRASE_EXTRACTION_FILE)

        if df.empty:
            raise HTTPException(status_code=500, detail="Extracted keyphrase DataFrame is empty.")

        # ✅ Ensure 'yake_keywords' and 'keybert_keyphrases' are lists
        if "yake_keywords" in df.columns:
            df["yake_keywords"] = df["yake_keywords"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        else:
            df["yake_keywords"] = [[]] * len(df)  # Fill with empty lists if missing

        if "keybert_keyphrases" in df.columns:
            df["keybert_keyphrases"] = df["keybert_keyphrases"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        else:
            df["keybert_keyphrases"] = [[]] * len(df)  # Fill with empty lists if missing

        # ✅ Apply EmbedRank
        df["embedrank_keywords"] = df.apply(
            lambda row: extract_embedrank_keywords(row["Sentence"], row["yake_keywords"], row["keybert_keyphrases"]),
            axis=1
        )

        # ✅ Save results to CSV
        df.to_csv(HYBRID_KEYWORDS_FILE_CSV, index=False, encoding="utf-8")

        print("✅ EmbedRank extraction completed successfully!")
        return {"success": True, "message": "EmbedRank extraction completed successfully!"}

    except Exception as e:
        print(f"❌ EmbedRank extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
