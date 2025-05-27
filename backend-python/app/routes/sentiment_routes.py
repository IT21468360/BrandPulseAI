#eng rou
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.controllers.sentiment_controller import predict_sentiment

router = APIRouter()

class SentimentInput(BaseModel):
    review: str
    aspect: str

class SentimentBatchInput(BaseModel):
    items: List[SentimentInput]

@router.post("/sentiment")
def get_sentiment(input: SentimentInput):
    sentiment, score = predict_sentiment(input.review, input.aspect)
    return {
        "review": input.review,
        "aspect": input.aspect,
        "sentiment": sentiment,
        "score": score
    }

@router.post("/sentiment-batch")
def get_batch_sentiments(input: SentimentBatchInput):
    results = []
    for item in input.items:
        sentiment, score = predict_sentiment(item.review, item.aspect)
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