from fastapi import HTTPException

from app.services.XAI.english.XAIService    import explain_with_lime, explain_with_shap
from app.services.XAI.english.report_service import full_report

async def xai_explain_controller(text: str, method: str, aspect: str = "general"):
    if not text:
        raise HTTPException(status_code=400, detail="`text` is required")

    m = method.lower()
    if m == "lime":
        return await explain_with_lime(text)
    if m == "shap":
        return await explain_with_shap(text)
    if m == "report":
        return full_report(text, aspect)

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported method '{method}'. Use 'lime', 'shap' or 'report'."
    )
