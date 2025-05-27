from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME", "BrandPulseAI")]
print("✅ results_controller.py LOADED ✅")

def load_aspects_from_mongo_DEBUGGING_NOW(brand, scrape_id):
    print(f"🔥 FILTER CHECK → brand={brand}, scrape_id={scrape_id}")

    english_cursor = db["English_Aspects"].find({
        "brand": brand,
        "scrape_id": scrape_id  # ✅ Do not forget this line!
    })

    sinhala_cursor = db["Sinhala_Aspects"].find({
        "brand": brand,
        "scrape_id": scrape_id  # ✅ And this too!
    })

    english_aspects = {}
    for doc in english_cursor:
        aspect = doc.get("aspect", "Others")
        english_aspects.setdefault(aspect, []).append(doc.get("comment", ""))

    sinhala_aspects = {}
    for doc in sinhala_cursor:
        aspect = doc.get("aspect", "Others")
        sinhala_aspects.setdefault(aspect, []).append(doc.get("comment", ""))

    print(f"✅ EN Result: {len(english_aspects)} aspects")
    print(f"✅ SI Result: {len(sinhala_aspects)} aspects")

    return {
        "English": [{"_id": k, "comments": v} for k, v in english_aspects.items()],
        "Sinhala": [{"_id": k, "comments": v} for k, v in sinhala_aspects.items()],
        "brand": brand,
        "scrape_id": scrape_id
    }
