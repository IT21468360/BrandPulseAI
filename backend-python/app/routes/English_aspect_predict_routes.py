from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.controllers.english_aspect_predict_controller import garbage_then_aspect


router = APIRouter()

class CombinedInput(BaseModel):
    comments: List[str]

@router.post("/garbage-then-aspect")
def classify_valid_and_aspect(input: CombinedInput):
    results = []
    for comment in input.comments:
        result = garbage_then_aspect(comment)
        results.append(result)
    return {"status": "success", "data": results}
