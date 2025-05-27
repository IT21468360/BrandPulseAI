# app/routes/report_routes.py

import os
from fastapi import APIRouter, HTTPException

from app.services.XAI.english.report_service import (
    generate_aspect_report,
    generate_lime,
    generate_shap,
    generate_wordcloud,
    REPORT_DIR,
)

router = APIRouter()
_last_overall: dict = {}

@router.post("/generate/all", summary="Generate the overall aspect report")
def generate_all():
    try:
        html_path = generate_aspect_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aspect report failed: {e}")

    charts = {
        "aspect_dist":  "/reports/aspect_distribution.png",
        "avg_likes":    "/reports/avg_likes.png",
        "likes_aspect": "/reports/likes_aspect_analysis.png",
        "neg_wc":       "/reports/negative_wordcloud.png",
        "pos_wc":       "/reports/positive_wordcloud.png",
    }

    _last_overall.clear()
    _last_overall.update({"html": html_path, "charts": charts})
    return _last_overall

@router.get("/aspect", summary="Fetch the most recently generated aspect report")
def get_aspect_report():
    if not _last_overall:
        raise HTTPException(
            status_code=404,
            detail="No aspect report found; please POST /generate/all first"
        )
    return _last_overall

@router.post(
    "/shaplime/generate",
    summary="(Re)generate all per-aspect LIME, SHAP & word-cloud files"
)
def generate_shaplime_all():
    # exactly these five aspects:
    aspects = [
        "Trust and Security",
        "Transaction and Payments",
        "Digital Banking Experience",
        "Loans and Credit Services",
        "Customer Support",
    ]
    errors = {}
    for a in aspects:
        try:
            generate_lime(a)
            generate_shap(a)
            generate_wordcloud(a)
        except Exception as e:
            errors[a] = str(e)

    if errors:
        # if any aspect failed, bubble up
        raise HTTPException(status_code=500, detail=f"Errors generating: {errors}")

    return {"generated": aspects}

@router.get("/shaplime", summary="List all aspect-wise LIME/SHAP/word-cloud samples")
def list_shaplime_samples():
    try:
        files = os.listdir(REPORT_DIR)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Cannot list reports: {e}")

    # find every lime_<key>.html
    aspects = sorted({
        fn[len("lime_"):-len(".html")]
        for fn in files
        if fn.startswith("lime_") and fn.endswith(".html")
    })

    out = []
    for key in aspects:
        human = key.replace("_", " ")
        out.append({
            "aspect":        human,
            "lime_html":     f"/reports/lime_{key}.html",
            "shap_html":     f"/reports/shap_{key}.html",
            "wordcloud_png": f"/reports/wordcloud_{key}.png",
        })
    return out
