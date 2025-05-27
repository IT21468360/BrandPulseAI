from fastapi import HTTPException
from lime.lime_text import LimeTextExplainer
import shap
from app.services.XAI.english.model_loader import predict_proba, tokenizer

CLASS_NAMES = ["Negative", "Neutral", "Positive"]

print("🔄 Initializing LIME & SHAP explainers...")

async def explain_with_lime(
    text: str,
    num_features: int = 10,
    num_samples:  int = 1000
) -> list[tuple[str, float]]:
    explainer = LimeTextExplainer(class_names=CLASS_NAMES)
    exp = explainer.explain_instance(
        text_instance=text,
        classifier_fn=predict_proba,
        num_features=num_features,
        num_samples=num_samples
    )
    return exp.as_list()

async def explain_with_shap(text: str) -> dict:
    try:
        masker    = shap.maskers.Text(tokenizer)
        explainer = shap.Explainer(predict_proba, masker, output_names=CLASS_NAMES)
        sv        = explainer([text])
        return {
            "tokens":      sv.data[0].tolist(),
            "base_values": sv.base_values[0].tolist(),
            "shap_values": [c.tolist() for c in sv.values[0]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

print("✅ LIME & SHAP explainers ready.")
