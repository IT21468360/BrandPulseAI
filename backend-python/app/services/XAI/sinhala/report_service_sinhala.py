# backend-python/app/services/XAI/sinhala/report_service_sinhala.py
import os
from datetime import datetime
from fastapi import HTTPException
from app.services.XAI.sinhala.XAIService_sinhala import (
    explain_with_lime_sinhala,
    explain_with_shap_sinhala
)

def full_report_sinhala(text: str, aspect: str = "general"):
    """
    Generates simple HTML fragments for LIME & SHAP in Sinhala,
    saves them under services/XAI/sinhala/reports, and returns
    the static URLs for your front‐end to fetch.
    """
    try:
        # Prepare output directory
        base_dir = os.path.dirname(__file__)
        rpt_dir  = os.path.join(base_dir, "reports")
        os.makedirs(rpt_dir, exist_ok=True)

        # Timestamp for unique filenames
        ts        = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        lime_name = f"lime_{ts}.html"
        shap_name = f"shap_{ts}.html"

        # 1) LIME
        lime_list = explain_with_lime_sinhala(text)
        lime_path = os.path.join(rpt_dir, lime_name)
        with open(lime_path, "w", encoding="utf-8") as f:
            f.write("<ul>\n")
            for feat, weight in lime_list:
                f.write(f"<li>{feat}: {weight:.4f}</li>\n")
            f.write("</ul>")

        # 2) SHAP
        shap_res = explain_with_shap_sinhala(text)
        shap_path = os.path.join(rpt_dir, shap_name)
        with open(shap_path, "w", encoding="utf-8") as f:
            # A very simple table
            f.write("<table border='1'><tr><th>Token</th>")
            for cls in ["Negative","Neutral","Positive"]:
                f.write(f"<th>{cls}</th>")
            f.write("</tr>\n")

            tokens = shap_res["tokens"]
            vals   = shap_res["shap_values"]  # list per class
            for i, tok in enumerate(tokens):
                f.write("<tr>")
                f.write(f"<td>{tok}</td>")
                for cls_vals in vals:
                    f.write(f"<td>{cls_vals[i]:.4f}</td>")
                f.write("</tr>\n")
            f.write("</table>")

        # Return the URLs (front‐end will fetch /reports/sinhala/{filename})
        return {
            "lime_html": f"/reports/sinhala/{lime_name}",
            "shap_html": f"/reports/sinhala/{shap_name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
