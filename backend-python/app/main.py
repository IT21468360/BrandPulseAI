import sys
import os
from dotenv import load_dotenv
from fastapi import FastAPI

# ✅ Load environment variables
load_dotenv()

# ✅ Ensure `app` directory is in Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# ✅ Ensure `services` and `routes` directories are in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "services"))
sys.path.append(os.path.join(os.path.dirname(__file__), "routes"))

# ✅ Import Routes & Services
from app.services.keyword.english.databaseService import db  # Fix import issue
from app.routes.keyword_routes import router as keyword_router
# ✅ Import routers
from app.routes.sentiment_routes import router as sentiment_router          # English Sentiment
from app.routes.sentiment_sinhala_routes import router as sinhala_router    # Sinhala Sentiment
print("🧪 Importing sentiment_csv_english_route...")
from app.routes.sentiment_csv_english_route import router as eng_csv_route
print("✅ Imported english_csv_route")

print("🧪 Importing sentiment_csv_sinhala_route...")
from app.routes.sentiment_csv_sinhala_route import router as sinhala_csv_router
print("✅ Imported sinhala_csv_route")


# ✅ Create FastAPI instance
app = FastAPI()

# ✅ Register Routes
app.include_router(keyword_router, prefix="/api/keyword", tags=["Keywords"])
# ✅ Register all routes
app.include_router(sentiment_router, prefix="/api/predict", tags=["English Sentiment"])
app.include_router(sinhala_router, prefix="/api/predict", tags=["Sinhala Sentiment"])
app.include_router(eng_csv_route, prefix="/api/csv", tags=["CSV English Prediction"])
app.include_router(sinhala_csv_router, prefix="/api/csv", tags=["CSV Sinhala Prediction"])

# ✅ Root Route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Python backend!"}

# ✅ Check MongoDB Connection on Startup
@app.on_event("startup")
async def startup_db_client():
    try:
        db.command("ping")
        print("✅ MongoDB Connection Successful!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {str(e)}")

# ✅ Root Route
@app.get("/")
def read_root():
    return {"message": "🔥 Multilingual Sentiment + CSV Prediction API is running!"}


# ✅ Run FastAPI App
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
