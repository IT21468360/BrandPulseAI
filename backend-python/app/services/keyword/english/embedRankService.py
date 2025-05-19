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

# ✅ Ensure `data` directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Load Sentence Transformer model
embed_model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-v3")

# ✅ EmbedRank function
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
    ranked_keywords = sorted(zip(keywords, similarity_scores.tolist()), key=lambda x: x[1], reverse=True)[:top_n]
    end_time = time.time()
    return [kw[0] for kw in ranked_keywords], (end_time - start_time)

# ✅ Main extraction route
@router.post("/embedrank-extract")
async def embedrank_extraction():
    try:
        # ✅ Load datasets
        if not all(os.path.exists(path) for path in [PARAGRAPH_FILE, YAKE_FILE, KEYBERT_FILE]):
            raise HTTPException(status_code=404, detail="One or more required files are missing.")

        df_para = pd.read_csv(PARAGRAPH_FILE)
        df_yake = pd.read_csv(YAKE_FILE)
        df_keybert = pd.read_csv(KEYBERT_FILE)

        # ✅ Ensure required columns
        if "Paragraph" not in df_para.columns:
            raise HTTPException(status_code=500, detail="'Paragraph' column missing.")

        df_yake["yake_keywords"] = df_yake["yake_keywords"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
        df_keybert["keybert_keyphrases"] = df_keybert["keybert_keyphrases"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

        # ✅ Merge all
        df = df_para.merge(df_yake, on="Paragraph", how="left").merge(df_keybert, on="Paragraph", how="left")

        # ✅ Apply EmbedRank
        df["embedrank_keywords"], df["embedrank_time"] = zip(*df.apply(
            lambda row: extract_embedrank_keywords(row["Paragraph"], row["yake_keywords"], row["keybert_keyphrases"]),
            axis=1
        ))

        # ✅ Save full CSV
        df.to_csv(EMBEDRANK_OUTPUT_CSV, index=False, encoding="utf-8")

        # ✅ Extract and save unique keywords
        all_embedrank_keyphrases = [
            kw.lower().strip()
            for keyphrases in df["embedrank_keywords"]
            if isinstance(keyphrases, list)
            for kw in keyphrases
        ]
        unique_embedrank_keyphrases = sorted(set(all_embedrank_keyphrases))

        with open(UNIQUE_EMBEDRANK_JSON, "w", encoding="utf-8") as f:
            json.dump(unique_embedrank_keyphrases, f, indent=4, ensure_ascii=False)

        # 🧾 Display sample
        print("\n🔟 Sample Unique EmbedRank Keyphrases:")
        for kw in unique_embedrank_keyphrases[:10]:
            print(f"- {kw}")

        return {
            "success": True,
            "message": "✅ EmbedRank keyphrase extraction completed.",
            "embedrank_csv_file": EMBEDRANK_OUTPUT_CSV,
            "unique_embedrank_json_file": UNIQUE_EMBEDRANK_JSON
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ EmbedRank extraction failed: {e}")
