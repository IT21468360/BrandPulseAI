from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.controllers.results_controller import load_aspects_from_mongo_DEBUGGING_NOW as load_aspects_from_mongo

router = APIRouter()

# ✅ This is now available as /api/results/aspects
@router.get("/aspects")
async def get_aspect_data(
    brand: str = Query(...),
    scrape_id: str = Query(...)
):
    print("✅ [results_routes.py] Loaded and active")
    print(f"📥 API HIT: /api/results/aspects?brand={brand}&scrape_id={scrape_id}")

    try:
        result = load_aspects_from_mongo(brand, scrape_id)

        # Debug output
        english_count = sum(len(aspect["comments"]) for aspect in result.get("English", []))
        sinhala_count = sum(len(aspect["comments"]) for aspect in result.get("Sinhala", []))
        print(f"🔎 Fetched English Comments: {english_count}")
        print(f"🔎 Fetched Sinhala Comments: {sinhala_count}")

        if "error" in result:
            print("🔥 MongoDB Error:", result["error"])
            return JSONResponse(status_code=500, content=result)

        print(f"✅ Loaded aspects for brand '{brand}' with scrape_id '{scrape_id}'")
        return JSONResponse(content=result)

    except Exception as e:
        print("🔥 Unexpected Error:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
