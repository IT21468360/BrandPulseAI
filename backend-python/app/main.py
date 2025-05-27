<<<<<<< Updated upstream
=======
import os
import sys
from dotenv import load_dotenv
>>>>>>> Stashed changes
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< Updated upstream
# Create a FastAPI app instance
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Python backend!"}
=======
# 1) Load environment vars
load_dotenv()

# 2) Make sure our app package is importable
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 3) Instantiate FastAPI
app = FastAPI(
    title="BrandPulseAI Service",
    version="1.0.0",
    description="Keyword management + XAI endpoints"
)

# 4) CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 5a) Serve static English reports under /reports
BASE_DIR      = os.path.dirname(__file__)
EN_REPORT_DIR = os.path.join(BASE_DIR, "services", "XAI", "english", "reports")
os.makedirs(EN_REPORT_DIR, exist_ok=True)
app.mount("/reports", StaticFiles(directory=EN_REPORT_DIR), name="reports")

# 5b) Serve static Sinhala reports under /reports/sinhala
SI_REPORT_DIR = os.path.join(BASE_DIR, "services", "XAI", "sinhala", "reports")
os.makedirs(SI_REPORT_DIR, exist_ok=True)
app.mount("/reports/sinhala", StaticFiles(directory=SI_REPORT_DIR), name="reports_sinhala")

# 6) Import & register routers
from app.routes.keyword_routes       import router as keyword_router
from app.routes.XAI_routes           import router as xai_router
from app.routes.report_routes        import router as report_router
from app.routes.XAI_sinhala_routes   import router as xai_sinhala_router
from app.routes.XAI_realtime_routes_SH  import router as realtime_excel_router_SH

app.include_router(keyword_router,      prefix="/api/keyword",     tags=["Keyword Management"])
app.include_router(xai_router,          prefix="/api/xai",         tags=["Explainability"])
# app.include_router(report_router,       prefix="/api/xai/reports", tags=["Reports"])
# app.include_router(xai_sinhala_router,  prefix="/api/xai/sinhala", tags=["Explainability (සිංහල)"])
# app.include_router(realtime_excel_router_SH, prefix="/api/xai",       tags=["XAI_Excel"])

# 7) Health check
@app.get("/health", summary="Health Check")
async def health():
    return {"status": "ok"}

# 8) On startup, verify MongoDB
@app.on_event("startup")
async def startup_db_client():
    from app.db.mongodb import get_db
    try:
        get_db().command("ping")
        print("✅ MongoDB Connection Successful!")
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")

# 9) Allow `python app/main.py` invocation
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
>>>>>>> Stashed changes
