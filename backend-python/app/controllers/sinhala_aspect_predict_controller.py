import os
import json
import torch
import re
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification

# ========== 🔹 Sinhala Garbage Classifier ==========
GARBAGE_MODEL_PATH = "Navojith012/sinhala_garbage_model"
garbage_tokenizer = XLMRobertaTokenizer.from_pretrained(GARBAGE_MODEL_PATH)
garbage_model = XLMRobertaForSequenceClassification.from_pretrained(GARBAGE_MODEL_PATH)
garbage_model.eval()

# ========== 🔹 Sinhala Aspect Classifier ==========
ASPECT_MODEL_PATH = "Navojith012/sinhala-aspect-classifier-v2"
aspect_tokenizer = XLMRobertaTokenizer.from_pretrained(ASPECT_MODEL_PATH)
aspect_model = XLMRobertaForSequenceClassification.from_pretrained(ASPECT_MODEL_PATH)
aspect_model.eval()

aspect_label_map = {
    0: "Customer Support",
    1: "Digital Banking Experience",
    2: "Loans and Credit Services",
    3: "Others",
    4: "Transactions and Payments",
    5: "Trust and Security"
}

# ========== 🧠 Load Aspect Lexicon ==========
LEXICON_PATH = "data/sinhala_aspect_lexicon.json"
try:
    with open(LEXICON_PATH, "r", encoding="utf-8") as f:
        aspect_lexicon = json.load(f)
except FileNotFoundError:
    aspect_lexicon = {}

# ========== 🧠 Load Garbage Lexicon ==========
GARBAGE_LEXICON_PATH = "data/garbage_lexicon_sinhala.json"
try:
    with open(GARBAGE_LEXICON_PATH, "r", encoding="utf-8") as f:
        garbage_lexicon = json.load(f).get("garbage_words", [])
except FileNotFoundError:
    garbage_lexicon = []

# ========== 🗑️ Sinhala Garbage Detection ==========
def is_sinhala_garbage(text: str, debug=False) -> bool:
    cleaned = text.strip().lower()

    # Lexicon-based garbage detection
    for word in garbage_lexicon:
        if word in cleaned:
            if debug:
                print(f"🗑️ Lexicon match → garbage word: '{word}' in comment: {text}")
            return True

    # Rule-based optional filters (optional)
    if len(cleaned) < 3:
        if debug: print("🗑️ Too short")
        return True
    if re.match(r"^[^\w\s]+$", cleaned):
        if debug: print("🗑️ Only symbols")
        return True

    # Model-based garbage detection
    inputs = garbage_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = garbage_model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
        if debug:
            print(f"🧠 Garbage model prediction: {prediction}")

    return prediction == 0  # 0 = garbage, 1 = valid

# ========== 📊 Sinhala Aspect Classification ==========
def classify_sinhala_aspect(text: str) -> str:
    inputs = aspect_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = aspect_model(**inputs)
        predicted_label = torch.argmax(outputs.logits, dim=1).item()
    return aspect_label_map.get(predicted_label, "Unknown")

# ========== 🔁 Combined Prediction ==========
def sinhala_garbage_then_aspect(text: str) -> dict:
    if is_sinhala_garbage(text):
        return {
            "comment": text,
            "label": "garbage",
            "aspect": None
        }

    # Step 1: Model prediction
    model_aspect = classify_sinhala_aspect(text)

    # Step 2: Lexicon override
    corrected_aspect = model_aspect
    for aspect, keywords in aspect_lexicon.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                corrected_aspect = aspect
                break
        if corrected_aspect != model_aspect:
            break

    return {
        "comment": text,
        "label": "valid",
        "aspect": corrected_aspect
    }
