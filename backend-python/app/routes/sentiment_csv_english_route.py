from fastapi import APIRouter, HTTPException
from app.controllers.english_csv_predictorController import process_english_csv_prediction

router = APIRouter()

@router.post("/english-csv-predict")
def run_english_sentiment_pipeline():
    """
    Reads the CSV file (Comment, Aspect), runs predictions,
    saves to MongoDB, and returns results.
    """
    try:
        result = process_english_csv_prediction()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
