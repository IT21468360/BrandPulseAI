from app.services.keyword.english.preprocessService import preprocess_text
from fastapi import HTTPException

async def process_preprocessing(raw_content):
    try:
        # ✅ Preprocess Text
        cleaned_text = preprocess_text(raw_content)
        if not cleaned_text:
            raise HTTPException(status_code=500, detail="Preprocessing failed or returned empty content.")

        return {"preprocessed_content": cleaned_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
