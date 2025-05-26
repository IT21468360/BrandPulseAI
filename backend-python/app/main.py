from fastapi import FastAPI
from dotenv import load_dotenv

<<<<<<< Updated upstream
# Create a FastAPI app instance
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Python backend!"}
=======
# ✅ Load environment variables
load_dotenv()

# ✅ Import routers
from app.routes.sentiment_routes import router as sentiment_router          # English Sentiment
from app.routes.sentiment_sinhala_routes import router as sinhala_router    # Sinhala Sentiment
from app.routes.sentiment_csv_english_route import router as eng_csv_route      # CSV Batch Prediction
from app.routes.sentiment_csv_sinhala_route import router as sinhala_csv_router

# ✅ Create only ONE FastAPI app instance
app = FastAPI()

# ✅ Register all routes
app.include_router(sentiment_router, prefix="/api/predict", tags=["English Sentiment"])
app.include_router(sinhala_router, prefix="/api/predict", tags=["Sinhala Sentiment"])
app.include_router(eng_csv_route, prefix="/api/csv", tags=["CSV English Prediction"])
app.include_router(sinhala_csv_router, prefix="/api/csv", tags=["CSV Sinhala Prediction"])


# ✅ Root Route
@app.get("/")
def read_root():
    return {"message": "🔥 Multilingual Sentiment + CSV Prediction API is running!"}
>>>>>>> Stashed changes
