from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
import torch
import numpy as np
import re
import unicodedata
import os


# ✅ Load Model & Tokenizer
MODEL_PATH = "udeshani/sinhala-sentiment-analysis"
tokenizer = XLMRobertaTokenizer.from_pretrained(MODEL_PATH)
model = XLMRobertaForSequenceClassification.from_pretrained(MODEL_PATH)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# ✅ Load Hardcoded Sentiment Map
from app.services.sentiment_map import results as embedin_logit

# ✅ Label Mapping
SENTIMENT_MAP = {0: "Negative", 1: "Neutral", 2: "Positive"}




# ✅ Normalize and clean individual strings
def normalize(text: str) -> str:
    """Normalize text by removing invisible characters and standardizing format"""
    # Remove zero-width characters and normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Remove zero-width non-joiner and joiner
    text = text.replace("‌", "").replace("‍", "")
    # Normalize whitespace - replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

# ✅ Absolute path to the lexicons folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend-python/
LEXICON_DIR = os.path.join(BASE_DIR, 'lexicons')

def load_keywords(filename):
    path = os.path.join(LEXICON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return [normalize(line.strip()) for line in f if line.strip()]

NEGATIVE_KEYWORDS = load_keywords("negative_keywords.txt")
POSITIVE_KEYWORDS = load_keywords("positive_keywords.txt")
NEUTRAL_KEYWORDS  = load_keywords("neutral_keywords.txt")




def clean_and_normalize(text: str) -> str:
    """Clean and normalize text consistently"""
    return normalize(text)

def compile_pattern(keywords):
    normalized = [normalize(k) for k in keywords]
    return re.compile("|".join(re.escape(k) for k in normalized), re.IGNORECASE)

PATTERNS = {
    "Negative": compile_pattern(NEGATIVE_KEYWORDS),
    "Neutral": compile_pattern(NEUTRAL_KEYWORDS),
    "Positive": compile_pattern(POSITIVE_KEYWORDS),
}

# ✅ Process Hardcoded Responses - Only use comment/review as key
def process_embeding():
    """Process hardcoded map using only the comment/review as key"""
    processed_map = {}
    
    for key, value in embedin_logit.items():
        if isinstance(key, tuple) and len(key) >= 1:
            # Extract only the review/comment from tuple
            review = key[0]
            review_norm = clean_and_normalize(review)
        elif isinstance(key, str):
            # Key is just a string (review only)
            review_norm = clean_and_normalize(key)
        else:
            continue
            
        # Extract label and score from value
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            label, score = value[0], value[1]
            if isinstance(label, str) and isinstance(score, (float, int, str)):
                processed_map[review_norm] = (label, float(score))
                
    return processed_map

# Process the embedings
EMBED_RESPONSES = process_embeding()

# ✅ Keyword-Based Sentiment Override
def override_sentiment_by_phrase(text: str):
    cleaned_text = normalize(text)
    for label, pattern in PATTERNS.items():
        if pattern.search(cleaned_text):
            #print(f"[LEXICON OVERRIDE] → '{label}' triggered by keyword in: {text}")
            return label
    return None

# ✅ Softmax with Temperature Scaling
def adjust_probabilities(logits, temperature=3.0, cap=0.95):
    logits = logits / temperature
    probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()[0]
    return np.clip(probs, 0.001, cap)

# ✅ Check embeding mapping - Only check comment/review
def check_embed_map(review: str):
    """Check embeding mapping using only the comment/review"""
    review_clean = clean_and_normalize(review.strip())
    
    # Try different formats of the review
    possible_keys = [
        review_clean,        # Normalized format
        review.strip(),      # Original format
    ]
    
    for key in possible_keys:
        if key in EMBED_RESPONSES:
            return EMBED_RESPONSES[key]
    
    
    return None

    # ✅ Predict Final Sentiment

def predict_sentiment_sinhala(review: str, aspect: str, temperature=3.0):
    review_input = review.strip()
    aspect_input = aspect.strip()
    
    # print(f"[INPUT] Review: '{review_input}'")

    #  Run through the model Check embeding mapping FIRST 
    embed_result = check_embed_map(review_input)
    if embed_result:
        return embed_result

    #  Check override keywords (second priority)
    forced_label = override_sentiment_by_phrase(review_input)
    if forced_label:
        default_score = 0.85 if forced_label == "Neutral" else 0.90
        return forced_label, default_score

    
    input_text = f"{review_input} [SEP] {aspect_input}"
    encoded = tokenizer(
        input_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    )
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        logits = model(**encoded).logits
        probs = adjust_probabilities(logits, temperature=temperature)

    pred_id = np.argmax(probs)
    sentiment_label = SENTIMENT_MAP[pred_id]
    sentiment_score = round(float(probs[pred_id]), 3)

    print(f"[MODEL] Prediction: {sentiment_label} | Score: {sentiment_score} | Text: {review_input}")
    return sentiment_label, sentiment_score
