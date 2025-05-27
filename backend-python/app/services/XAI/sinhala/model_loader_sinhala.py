# backend-python/app/services/XAI/sinhala/model_loader_sinhala.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax

# Load your Sinhala model ID from .env
HF_MODEL_SINHALA = os.getenv("HF_MODEL_SINHALA")
if not HF_MODEL_SINHALA:
    raise RuntimeError("`HF_MODEL_SINHALA` not set in environment")

# Load tokenizer & model
# Use the slow Python tokenizer to avoid Rust pretokenizer errors
# (e.g., on Windows without symlink support)
tokenizer_sinhala = AutoTokenizer.from_pretrained(
    HF_MODEL_SINHALA,
    use_fast=False
)
model_sinhala = AutoModelForSequenceClassification.from_pretrained(
    HF_MODEL_SINHALA
)
# Ensure model is in eval mode and on CPU
detached_model = model_sinhala.eval()
detached_model.to('cpu')


def predict_proba_sinhala(texts):
    """
    texts: List[str] or single str
    returns: np.ndarray shape (n_texts, n_classes)
    """
    if isinstance(texts, str):
        texts = [texts]
    # ensure all items are strings
    texts = [str(t) for t in texts]

    encodings = tokenizer_sinhala(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=256
    )
    with torch.no_grad():
        outputs = model_sinhala(**encodings)
        probs = softmax(outputs.logits, dim=1)
    return probs.cpu().numpy()
