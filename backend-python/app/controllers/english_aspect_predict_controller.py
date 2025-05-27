from transformers import BertTokenizer, BertForSequenceClassification
import torch

# ==============================
# 🔹 Garbage Classification Model
# ==============================

GARBAGE_MODEL_PATH = "Navojith012/english-garbage-classifier"

garbage_tokenizer = BertTokenizer.from_pretrained(GARBAGE_MODEL_PATH)
garbage_model = BertForSequenceClassification.from_pretrained(GARBAGE_MODEL_PATH)
garbage_model.eval()

def is_garbage_comment(text: str) -> bool:
    inputs = garbage_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = garbage_model(**inputs)
        predicted_label = torch.argmax(outputs.logits, dim=1).item()
    return predicted_label == 0  # ✅ correct logic


# ==============================
# 🔹 Aspect Classification Model
# ==============================

ASPECT_MODEL_PATH = "Navojith012/english-aspect-classifier"

aspect_tokenizer = BertTokenizer.from_pretrained(ASPECT_MODEL_PATH)
aspect_model = BertForSequenceClassification.from_pretrained(ASPECT_MODEL_PATH)
aspect_model.eval()

ASPECT_LABELS = {
    0: "Customer Support",
    1: "Digital Banking Experience",
    2: "Loans and Credit Services",
    3: "Others",
    4: "Transaction, Payments and Accounts",
    5: "Trust and Security"
}

def classify_aspect(text: str) -> str:
    inputs = aspect_tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = aspect_model(**inputs)
        predicted_label = torch.argmax(outputs.logits, dim=1).item()
    return ASPECT_LABELS.get(predicted_label, "Unknown")


# ==============================
# 🔁 Combined Pipeline
# ==============================

def garbage_then_aspect(text: str) -> dict:
    is_garbage = is_garbage_comment(text)
    if is_garbage:
        return {
            "comment": text,
            "label": "garbage",
            "aspect": None
        }
    else:
        aspect = classify_aspect(text)
        return {
            "comment": text,
            "label": "valid",
            "aspect": aspect
        }
