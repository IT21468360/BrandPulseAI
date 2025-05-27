# backend-python/app/services/XAI/english/model_loader.py
import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv

load_dotenv()
MODEL_ID = os.getenv("HF_MODEL")
DEVICE   = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("🔄 Loading tokenizer and model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
model.to(DEVICE).eval()

print(f"✅ Loaded `{MODEL_ID}` on {DEVICE}.")

def predict_proba(texts, *args, **kwargs):
    """
    SHAP may call this with:
      - texts=str
      - texts=[str,...]
      - texts=np.ndarray([...]) of tokens
      - texts=first_arg, args=(second_arg, third_arg, ...) from MaskedModel
    This will normalize everything into List[str].
    """
    # 1) If SHAP gave us multiple positional args, stitch them into one sequence list
    if args and not isinstance(texts, (list, tuple, np.ndarray)):
        texts = [texts] + list(args)

    # 2) If it's a numpy array, turn it into a Python list
    if isinstance(texts, np.ndarray):
        texts = texts.tolist()

    # 3) Now build a uniform batch of plain strings
    batch = []
    for t in texts if isinstance(texts, (list, tuple)) else [texts]:
        if isinstance(t, (list, tuple)):
            # sequence of tokens ➔ re-join to a string
            batch.append(" ".join(map(str, t)))
        else:
            batch.append(str(t))

    # 4) Tokenize & predict
    inputs = tokenizer(
        batch,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128
    ).to(DEVICE)

    with torch.no_grad():
        logits = model(**inputs).logits

    return torch.softmax(logits, dim=1).cpu().numpy()