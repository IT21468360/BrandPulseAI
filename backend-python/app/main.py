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


# ✅ Create FastAPI instance
app = FastAPI()

# ✅ Register Routes
app.include_router(keyword_router, prefix="/api/keyword", tags=["Keywords"])

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

# ✅ Run FastAPI App
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
