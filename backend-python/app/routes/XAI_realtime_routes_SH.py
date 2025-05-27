from fastapi import APIRouter, Query
from app.controllers.XAI_realtime_controller_SH import sample_explain_controller_SH

router = APIRouter()

@router.get(
    "/realtime-excel-samples",
    summary="One random sample per aspect (LIME+SHAP) from Excel"
)
async def get_realtime_excel_samples_SH(
    limit: int = Query(None, description="Max number of aspects to process")
):
    # if you want only first 5: /realtime-excel-samples?limit=5
    return await sample_explain_controller_SH(limit)
