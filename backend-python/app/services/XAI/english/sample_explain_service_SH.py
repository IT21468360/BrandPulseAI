import os
import uuid
import pandas as pd
import shap
from lime.lime_text import LimeTextExplainer

from app.services.XAI.english.model_loader import predict_proba, tokenizer
from app.services.XAI.english.report_service import REPORT_DIR, _save_html

# locate your Excel
BASE_DIR     = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../../.."))
DATA_FILE    = os.path.join(
    BACKEND_ROOT, "data", "Sentiment", "English",
    "Updated_Final_Aspect_Classification new english.xlsx"
)

CLASS_NAMES = ["Negative", "Neutral", "Positive"]

def generate_excel_explanations_SH(limit: int = None) -> list[dict]:
    if not os.path.isfile(DATA_FILE):
        raise FileNotFoundError(f"Missing Excel at {DATA_FILE}")

    # 1) delete any old Excel-LIME/SHAP files
    for fn in os.listdir(REPORT_DIR):
        if fn.startswith("excel_lime_") or fn.startswith("excel_shap_"):
            try:
                os.remove(os.path.join(REPORT_DIR, fn))
            except Exception:
                pass

    df      = pd.read_excel(DATA_FILE, engine="openpyxl")
    aspects = list(df["Aspect"].dropna().unique())
    if limit:
        aspects = aspects[:limit]

    lime_exp = LimeTextExplainer(class_names=CLASS_NAMES)
    outputs  = []

    for aspect in aspects:
        sub = df[df["Aspect"] == aspect]
        if sub.empty:
            continue

        # pick exactly one random comment
        row  = sub.sample(n=1, random_state=42).iloc[0]
        text = str(row["Modified_Comment"])

        # ── generate LIME HTML ──────────────────────────────
        exp      = lime_exp.explain_instance(
                     text,
                     predict_proba,
                     num_features=10,
                     num_samples=500
                   )
        fn_lime  = f"excel_lime_{aspect.replace(' ','_')}_{uuid.uuid4().hex}_SH"
        path_lime = _save_html(fn_lime, exp.as_html())

        # ── generate SHAP force plot HTML ────────────────────
        masker    = shap.maskers.Text(tokenizer)
        explainer = shap.Explainer(
                      predict_proba,
                      masker,
                      output_names=CLASS_NAMES
                    )
        sv        = explainer([text])
        fp        = shap.plots.force(
                      sv.base_values[0][2],
                      sv.values[0][:,2],
                      sv.data[0],
                      matplotlib=False
                    )
        fn_shap   = f"excel_shap_{aspect.replace(' ','_')}_{uuid.uuid4().hex}_SH"
        full_shap = os.path.join(REPORT_DIR, fn_shap + ".html")
        shap.save_html(full_shap, fp)
        path_shap = f"/reports/{fn_shap}.html"

        outputs.append({
            "aspect":    aspect,
            "text":      text,
            "lime_html": path_lime,
            "shap_html": path_shap
        })

    return outputs


