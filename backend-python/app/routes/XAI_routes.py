import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.XAI import xai_explain_controller
from app.services.XAI.english.sample_explain_service_SH import generate_excel_explanations_SH

router = APIRouter()

# ── your existing /explain & /history routes ─────────────────────────────────
class ExplainRequest(BaseModel):
    text:   str
    method: str = "lime"
    aspect: str = "general"

@router.post("/explain", summary="Run LIME/SHAP or full‐report")
async def explain(req: ExplainRequest):
    return await xai_explain_controller(req.text, req.method, req.aspect)

@router.get("/history", summary="List past explanations")
async def history(limit: int = 10):
    from app.db.mongodb import get_db
    docs = list(
        get_db().explainabilities
             .find().sort("created_at",-1)
             .limit(limit)
    )
    for d in docs: d["_id"] = str(d["_id"])
    return docs

# ── NEW endpoint for “Excel → one random LIME/SHAP per aspect” ──────────────
@router.get(
    "/realtime-excel-samples",
    summary="One random sample per aspect (LIME+SHAP) from Excel"
)
def realtime_excel_samples():
    try:
        return generate_excel_explanations_SH()
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=500, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to gen samples: {e}")
