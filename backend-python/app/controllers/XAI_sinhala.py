# backend-python/app/controllers/XAI_sinhala.py
from fastapi import HTTPException
from app.services.XAI.sinhala.XAIService_sinhala import (
    explain_with_lime_sinhala,
    explain_with_shap_sinhala
)
from app.services.XAI.sinhala.report_service_sinhala import full_report_sinhala

async def xai_explain_controller_sinhala(text: str, method: str, aspect: str = "general"):
    if not text:
        raise HTTPException(status_code=400, detail="`text` is required")

    m = method.lower()
    if m == "lime":
        return await explain_with_lime_sinhala(text)
    if m == "shap":
        return await explain_with_shap_sinhala(text)
    if m == "report":
        # generate full HTML & return static‐file URL paths
        return full_report_sinhala(text, aspect)

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported method '{method}'. Use 'lime', 'shap' or 'report'."
    )
