from fastapi import APIRouter, HTTPException
from app.controllers.sinhala_csv_predictorController import process_sinhala_csv_prediction

router = APIRouter()

@router.post("/sinhala-csv-predict")
def run_sinhala_pipeline():
    try:
        result = process_sinhala_csv_prediction()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
