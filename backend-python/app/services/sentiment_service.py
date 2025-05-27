from transformers import BertTokenizer, BertForSequenceClassification
import torch
import numpy as np

MODEL_PATH = "udeshani/english-sentiment-analysis"

tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

SENTIMENT_MAP = {0: "Negative", 1: "Neutral", 2: "Positive"}

POSITIVE_KEYWORDS = [
    "super helpful", "very professional", "quick resolution", "sorted my issue",
    "amazing support", "great service", "excellent help", "prompt response", "resolved quickly"
]

NEGATIVE_KEYWORDS = [
    "no response", "not working", "very disappointed", "unacceptable", "still not fixed",
    "worst experience", "waste of time", "ignored", "useless", "kept waiting"
]

def detect_mixed_sentiment(text):
    keywords = ["but", "however", "although", "still", "even though", "on the other hand"]
    return any(k in text.lower() for k in keywords)

def contains_keywords(text, keyword_list):
    return any(phrase in text.lower() for phrase in keyword_list)

def adjust_probabilities(logits, temperature=3.2, cap=0.95):
    logits = logits / temperature
    probs = torch.nn.functional.softmax(logits, dim=1).cpu().numpy()[0]
    return np.clip(probs, 0.001, cap)

def apply_boost(sentiment, score, text):
    if sentiment == "Positive" and contains_keywords(text, POSITIVE_KEYWORDS):
        score = min(round(score + (0.05 if score < 0.85 else 0.02), 3), 0.95)
    elif sentiment == "Negative" and contains_keywords(text, NEGATIVE_KEYWORDS):
        score = min(round(score + (0.05 if score < 0.85 else 0.02), 3), 0.95)
    return score

def predict_sentiment(text: str, aspect: str):
    input_text = f"{text} [SEP] {aspect}"

    encoded = tokenizer.encode_plus(
        input_text,
        add_special_tokens=True,
        max_length=128,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        outputs = model(**encoded)
        logits = outputs.logits

    temp = 6.0 if detect_mixed_sentiment(text) else 3.2
    probs = adjust_probabilities(logits, temperature=temp)

    pred_idx = np.argmax(probs)
    sentiment = SENTIMENT_MAP[pred_idx]
    score = round(float(probs[pred_idx]), 3)

    # Apply smart boosting
    score = apply_boost(sentiment, score, text)

    # Clamp Neutral score to avoid 0.91-type inflation
    if sentiment == "Neutral":
        score = min(score, 0.85)

    return sentiment, score
