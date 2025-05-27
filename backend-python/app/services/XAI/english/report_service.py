import os
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from lime.lime_text import LimeTextExplainer
from wordcloud import WordCloud

# your model + tokenizer
from app.services.XAI.english.model_loader import tokenizer, predict_proba
# Mongo helper
from app.db.mongodb import get_db

# ─── CONFIGURE PATHS ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../../.."))
DATA_FILE = os.path.join(
    BACKEND_ROOT, "data", "Sentiment", "English",
    "Updated_Final_Aspect_Classification new english.xlsx"
)
if not os.path.isfile(DATA_FILE):
    raise FileNotFoundError(f"Dataset not found at: {DATA_FILE}")

REPORT_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

CLASS_NAMES = ["Negative", "Neutral", "Positive"]

def _save_html(name: str, html: str) -> str:
    fn = f"{name}.html"
    path = os.path.join(REPORT_DIR, fn)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"/reports/{fn}"

def _save_fig(name: str, fig) -> str:
    fn = f"{name}.png"
    path = os.path.join(REPORT_DIR, fn)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return f"/reports/{fn}"

# ─── 1) OVERALL ASPECT REPORT ────────────────────────────────────────────────────
def generate_aspect_report() -> str:
    df = pd.read_excel(DATA_FILE, engine="openpyxl")

    selected_aspects = [
        "Trust and Security",
        "Transaction and Payments",
        "Digital Banking Experience",
        "Loans and Credit Services",
        "Customer Support"
    ]

    # TF-IDF helper
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    def get_top_keywords(texts, n=5):
        if not texts:
            return []
        vect = TfidfVectorizer(stop_words="english", max_features=50)
        M = vect.fit_transform(texts)
        scores = np.array(M.sum(axis=0)).ravel()
        feats  = np.array(vect.get_feature_names_out())
        idx    = scores.argsort()[::-1][:n]
        return feats[idx].tolist()

    # build HTML
    report_html = """
    <html><head><meta charset="utf-8"/><title>Aspect-Based Analysis Report</title>
      <style>
        body { font-family: Arial, sans-serif; background:#f5f7fa; padding:20px; }
        h1 { color:#0B1F3F; }
        .aspect { background:white; border-radius:8px; margin:20px 0; padding:16px;
                  box-shadow:0 2px 4px rgba(0,0,0,0.1); }
        .aspect-header {
          background-color: #0B1F3F;
          color: white;
          padding: 8px;
          border-radius: 4px;
          margin: -16px -16px 12px -16px;
          font-size: 1.1em;
          font-weight: bold;
        }
        .metrics { margin:8px 0; }
        .section-title { color:#0B1F3F; font-weight:bold; margin-top:12px; }
        ul { margin:4px 0 12px 20px; }
        .advice { font-style:italic; margin-top:12px; }
      </style>
    </head><body>
      <h1>Aspect-Based Analysis Report</h1>
    """

    for aspect in selected_aspects:
        sub = df[df["Aspect"] == aspect]
        total = len(sub)
        counts = sub["Sentiment"].value_counts().to_dict()
        pos = counts.get("Positive", 0)
        neg = counts.get("Negative", 0)
        neu = counts.get("Neutral", 0)

        if total > 0:
            pos_pct = pos/total*100
            neg_pct = neg/total*100
            neu_pct = neu/total*100
        else:
            pos_pct = neg_pct = neu_pct = 0

        pos_texts = sub[sub["Sentiment"]=="Positive"]["Modified_Comment"].astype(str).tolist()
        neg_texts = sub[sub["Sentiment"]=="Negative"]["Modified_Comment"].astype(str).tolist()
        pos_keys  = get_top_keywords(pos_texts,5)
        neg_keys  = get_top_keywords(neg_texts,5)

        highlights   = [f"Many customers appreciate the {k} feature." for k in pos_keys[:3]]
        improvements = [f"Some customers expressed concerns about {k}."     for k in neg_keys[:3]]

        advice = (
            f"The overall feedback for {aspect} is positive. Keep up the good work in this area."
            if pos_pct >= neg_pct else
            f"The overall feedback for {aspect} indicates room for improvement. Address the key issues raised."
        )

        report_html += f"""
        <div class="aspect">
          <div class="aspect-header">--- {aspect} ---</div>
          <div class="metrics"><strong>Sentiment Counts:</strong> {{'Positive': {pos}, 'Negative': {neg}, 'Neutral': {neu}}}</div>
          <div class="metrics"><strong>Top Keywords (Positive):</strong> {pos_keys}</div>
          <div class="metrics"><strong>Top Keywords (Negative):</strong> {neg_keys}</div>
          <div class="section-title">Highlights:</div>
          <ul>""" + "".join(f"<li>{h}</li>" for h in highlights) + "</ul>" + \
        f"""
          <div class="section-title">Areas Needing Improvement:</div>
          <ul>""" + "".join(f"<li>{i}</li>" for i in improvements) + "</ul>" + \
        f"""
          <div class="advice"><strong>Advice:</strong> {advice}</div>
          <div class="metrics">(Positive: {pos_pct:.2f}%, Negative: {neg_pct:.2f}%, Neutral: {neu_pct:.2f}%)</div>
        </div>
        """

    report_html += "</body></html>"

    html_path = _save_html("sentiment_analysis_report", report_html)

    # ─── then charts & clouds ─────────────────────────────────────────────────────
    dist = df.groupby("Aspect")["Sentiment"].value_counts().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(8,5))
    dist.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Sentiment Distribution by Aspect")
    _save_fig("aspect_distribution", fig)

    if "Likes" in df.columns:
        import seaborn as sns
        avg = df.groupby("Sentiment")["Likes"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(6,4))
        sns.barplot(x="Sentiment", y="Likes", data=avg, ax=ax)
        ax.set_title("Average Likes by Sentiment")
        _save_fig("avg_likes", fig)

        likes_as = df.groupby(["Aspect","Sentiment"])["Likes"].mean().unstack().fillna(0)
        fig, ax = plt.subplots(figsize=(8,5))
        likes_as.plot(kind="bar", ax=ax)
        ax.set_title("Avg Likes by Aspect & Sentiment")
        _save_fig("likes_aspect_analysis", fig)

    for sentiment in ["Positive","Negative"]:
        texts = df[df["Sentiment"]==sentiment]["Modified_Comment"].astype(str).tolist()
        if texts:
            wc = WordCloud(width=800, height=400, background_color="white")\
                    .generate(" ".join(texts))
            fig, ax = plt.subplots(figsize=(8,4))
            ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
            _save_fig(f"{sentiment.lower()}_wordcloud", fig)

    return html_path

# ─── 2) LIME EXPLANATION ─────────────────────────────────────────────────────────
def generate_lime(aspect: str) -> str:
    df = pd.read_excel(DATA_FILE, engine="openpyxl")
    txt = df[df["Aspect"]==aspect].iloc[0]["Modified_Comment"]
    exp = LimeTextExplainer(class_names=CLASS_NAMES)\
          .explain_instance(txt, predict_proba, num_features=10, num_samples=500)
    return _save_html(f"lime_{aspect.replace(' ','_')}", exp.as_html())

# ─── 3) SHAP EXPLANATION ─────────────────────────────────────────────────────────
def generate_shap(aspect: str) -> str:
    df = pd.read_excel(DATA_FILE, engine="openpyxl")
    txt = df[df["Aspect"]==aspect].iloc[0]["Modified_Comment"]
    masker    = shap.maskers.Text(tokenizer)
    explainer = shap.Explainer(predict_proba, masker, output_names=CLASS_NAMES)
    sv        = explainer([txt])
    fn        = f"shap_{aspect.replace(' ','_')}.html"
    full      = os.path.join(REPORT_DIR, fn)
    shap.save_html(full, shap.plots.force(
        sv.base_values[0][2], sv.values[0][:,2], sv.data[0], matplotlib=False
    ))
    return f"/reports/{fn}"

# ─── 4) WORDCLOUD ────────────────────────────────────────────────────────────────
def generate_wordcloud(aspect: str) -> str:
    df  = pd.read_excel(DATA_FILE, engine="openpyxl")
    txt = str(df[df["Aspect"]==aspect].iloc[0]["Modified_Comment"])
    wc  = WordCloud(width=600, height=300, background_color="white")\
            .generate(txt)
    fig, ax = plt.subplots(figsize=(6,3))
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    return _save_fig(f"wordcloud_{aspect.replace(' ','_')}", fig)

# ─── 5) FULL-REPORT WRAPPER ──────────────────────────────────────────────────────
def full_report(text: str, aspect: str) -> dict:
    lime_p = generate_lime(aspect)
    shap_p = generate_shap(aspect)
    wc_p   = generate_wordcloud(aspect)

    db  = get_db().explainabilities
    db.insert_one({
        "aspect":        aspect,
        "text":          text,
        "lime_html":     lime_p,
        "shap_html":     shap_p,
        "wordcloud_png": wc_p,
        "created_at":    datetime.utcnow()
    })
    return {"lime": lime_p, "shap": shap_p, "wordcloud": wc_p}
