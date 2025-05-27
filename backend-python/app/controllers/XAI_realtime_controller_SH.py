from fastapi import HTTPException
from app.services.XAI.english.sample_explain_service_SH import generate_excel_explanations_SH

async def sample_explain_controller_SH(limit: int = None):
    try:
        # return one sample per aspect (limit optional)
        return generate_excel_explanations_SH(limit)
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=500, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to gen samples: {e}")
