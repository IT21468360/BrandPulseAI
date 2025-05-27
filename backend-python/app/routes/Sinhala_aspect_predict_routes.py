from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.controllers.sinhala_aspect_predict_controller import (
    is_sinhala_garbage,
    classify_sinhala_aspect,
    sinhala_garbage_then_aspect
)


router = APIRouter()

class SinhalaInput(BaseModel):
    comments: List[str]

# # 🔹 Garbage Classifier Only
# @router.post("/sinhala/garbage")
# def sinhala_garbage_filter(input: SinhalaInput):
#     results = []
#     for comment in input.comments:
#         label = "garbage" if is_sinhala_garbage(comment) else "valid"
#         results.append({"comment": comment, "label": label})
#     return {"status": "success", "data": results}

# # 🔹 Aspect Classifier Only
# @router.post("/sinhala/aspect")
# def sinhala_aspect_predict(input: SinhalaInput):
#     results = []
#     for comment in input.comments:
#         aspect = classify_sinhala_aspect(comment)
#         results.append({"comment": comment, "aspect": aspect})
#     return {"status": "success", "data": results}

# 🔁 Combined: Garbage Filter + Aspect Classification
@router.post("/sinhala/combined")
def sinhala_combined_predict(input: SinhalaInput):
    results = []
    for comment in input.comments:
        result = sinhala_garbage_then_aspect(comment)
        results.append(result)
    return {"status": "success", "data": results}
