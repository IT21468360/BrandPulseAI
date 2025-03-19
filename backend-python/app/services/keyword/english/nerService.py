import os
import json
import spacy
import pandas as pd
from fastapi import APIRouter, HTTPException

# Initialize FastAPI Router
router = APIRouter()

# Define paths for input/output files
CLEANED_SCRAPED_FILE = os.path.join("data", "cleaned_scraped_content.json")
NER_EXTRACTED_FILE_JSON = os.path.join("data", "ner_extracted_sentences.json")
NER_EXTRACTED_FILE_CSV = os.path.join("data", "ner_extracted_sentences.csv")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Load Fine-Tuned SpaCy NER Model
fine_tuned_model_path = "./app/models/finetuned_spacy_ner"  # Update path if necessary
try:
    nlp = spacy.load(fine_tuned_model_path)
except Exception as e:
    raise RuntimeError(f"Failed to load NER model: {e}")

def extract_ner_tags(sentence):
    """
    Extracts Named Entities using the fine-tuned SpaCy NER model.
    """
    doc = nlp(sentence)
    return [[ent.text, ent.label_, ent.start_char, ent.end_char] for ent in doc.ents]

# @router.post("/ner-extract")
async def ner_extraction():
    """
    Loads cleaned sentences, extracts Named Entities, and saves results.
    """
    try:
        # Load preprocessed content from JSON
        if not os.path.exists(CLEANED_SCRAPED_FILE):
            raise HTTPException(status_code=404, detail="Preprocessed content file not found.")

        with open(CLEANED_SCRAPED_FILE, "r", encoding="utf-8") as f:
            cleaned_content = json.load(f)

        if not cleaned_content:
            raise HTTPException(status_code=500, detail="No data found in preprocessed file.")

        # Convert JSON to DataFrame
        df = pd.DataFrame(cleaned_content, columns=["Sentence"])

        if df.empty:
            raise HTTPException(status_code=500, detail="DataFrame is empty after preprocessing.")

        # Extract Named Entities
        df["entities"] = df["Sentence"].apply(extract_ner_tags)

        # Save results
        df.to_csv(NER_EXTRACTED_FILE_CSV, index=False, encoding="utf-8")

        return {
            "success": True,
            "message": "NER extraction completed successfully!",
            "ner_csv_file": NER_EXTRACTED_FILE_CSV
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

