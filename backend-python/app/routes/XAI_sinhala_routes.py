# backend-python/app/routes/XAI_sinhala_routes.py
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from app.controllers.XAI_sinhala import xai_explain_controller_sinhala
from app.db.mongodb import get_db

router = APIRouter()

class ExplainSinhalaRequest(BaseModel):
    text:   str = Field(..., example="මම මෙම විශේෂාංගය ප්‍රීතිමත් විඳිමි!")
    method: str = Field(
        default="lime",
        example="report",
        description="Choose 'lime', 'shap' or 'report'"
    )
    aspect: str = Field(default="general", description="Aspect label for grouping")

@router.post(
    "/explain",
    summary="Generate LIME/SHAP explanation or full report (Sinhala)"
)
async def explain_route_sinhala(req: ExplainSinhalaRequest):
    return await xai_explain_controller_sinhala(req.text, req.method, req.aspect)

@router.get(
    "/history",
    summary="List past Sinhala explanations from MongoDB"
)
async def history_sinhala(limit: int = Query(10, ge=1, le=100)):
    """
    Returns the most recent `limit` explainability runs for Sinhala.
    """
    col  = get_db().explainabilities_sinhala
    docs = list(col.find().sort("created_at", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
        d["created_at"] = d["created_at"].isoformat()
        # prepend static mount for front-end if needed
    return docs
