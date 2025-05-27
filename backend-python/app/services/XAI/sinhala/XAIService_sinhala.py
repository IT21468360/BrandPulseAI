# backend-python/app/services/XAI/sinhala/XAIService_sinhala.py
from fastapi import HTTPException
from lime.lime_text import LimeTextExplainer
import shap
from app.services.XAI.sinhala.model_loader_sinhala import predict_proba_sinhala, tokenizer_sinhala

CLASS_NAMES_SINHALA = ["Negative", "Neutral", "Positive"]

print("🔄 Initializing Sinhala LIME & SHAP explainers...")

async def explain_with_lime_sinhala(
    text: str,
    num_features: int = 10,
    num_samples:  int = 1000
) -> list[tuple[str, float]]:
    explainer = LimeTextExplainer(class_names=CLASS_NAMES_SINHALA)
    exp = explainer.explain_instance(
        text_instance=text,
        classifier_fn=predict_proba_sinhala,
        num_features=num_features,
        num_samples=num_samples
    )
    return exp.as_list()

async def explain_with_shap_sinhala(text: str) -> dict:
    try:
        masker    = shap.maskers.Text(tokenizer_sinhala)
        explainer = shap.Explainer(
            predict_proba_sinhala,
            masker,
            output_names=CLASS_NAMES_SINHALA
        )
        sv = explainer([text])

        data       = sv.data[0]            # tokens
        base_vals  = sv.base_values[0]     # expected values
        shap_vals  = sv.values[0]          # shape=(n_tokens, n_classes)

        return {
            "tokens":      data.tolist(),
            "base_values": base_vals.tolist(),
            "shap_values": [cls.tolist() for cls in shap_vals.T]  # list per class
        }

    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

print("✅ Sinhala LIME & SHAP explainers ready.")
