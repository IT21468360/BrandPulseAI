from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.controllers.sentiment_sinhala_controller import predict_sentiment_sinhala

router = APIRouter()

class SentimentInputSinhala(BaseModel):
    review: str
    aspect: str

class SentimentBatchInputSinhala(BaseModel):
    items: List[SentimentInputSinhala]

@router.post("/sinhala-sentiment")
def get_sentiment_sinhala(input: SentimentInputSinhala):
    sentiment, score = predict_sentiment_sinhala(input.review, input.aspect)
    return {
        "review": input.review,
        "aspect": input.aspect,
        "sentiment": sentiment,
        "score": score
    }

@router.post("/sinhala-sentiment-batch")
def get_batch_sentiments_sinhala(input: SentimentBatchInputSinhala):
    results = []
    for item in input.items:
        sentiment, score = predict_sentiment_sinhala(item.review, item.aspect)
        results.append({
            "review": item.review,
            "aspect": item.aspect,
            "sentiment": sentiment,
            "score": score
        })
    return {
        "status": "success",
        "data": results
    }
