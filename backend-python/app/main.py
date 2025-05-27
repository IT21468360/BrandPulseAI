import sys
import os
from fastapi.middleware.cors import CORSMiddleware
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


# ✅ Create FastAPI instance
app = FastAPI()

# ✅ Register Routes
app.include_router(keyword_router, prefix="/api/keyword", tags=["Keywords"])

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# ✅ Import routers
from app.routes.youtube_scraper_routes import router as youtube_scraper_router
from app.routes.English_aspect_predict_routes import router as english_router
from app.routes.Sinhala_aspect_predict_routes import router as sinhala_router
from app.routes.aspect_scraper_routes import router as aspect_scraper_router
from app.routes.results_routes import router as results_router
from app.routes import youtube_meta_routes

# ✅ Mount routers
app.include_router(youtube_scraper_router, prefix="/api/youtube", tags=["YouTube Scraper"])
app.include_router(english_router, prefix="/api/predict", tags=["English Aspect Prediction"])
app.include_router(sinhala_router, prefix="/api/predict", tags=["Sinhala Aspect Prediction"])
app.include_router(aspect_scraper_router, prefix="/api", tags=["Aspect Classification"])
app.include_router(results_router, prefix="/api/results", tags=["Results"])  # ✅ KEEP this!

from app.routes.youtube_meta_routes import router as meta_router
app.include_router(meta_router)

# ✅ Run FastAPI App
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
