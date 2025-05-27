import os
import pandas as pd
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

def get_latest_csv(path: str):
    files = [f for f in os.listdir(path) if f.endswith('.csv')]
    if not files:
        return None
    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(path, f)))
    return os.path.join(path, latest)


@router.get("/api/aspects")
async def get_aspect_data():
    try:
        current_dir = os.path.dirname(__file__)
        base_path = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "aspect_classification"))
        folders = ["English", "Sinhala"]

        print(f"[DEBUG] Base path: {base_path}")
        all_aspects = []

        for lang in folders:
            folder_path = os.path.join(base_path, lang)
            print(f"[DEBUG] Checking folder: {folder_path}")
            latest_file = get_latest_csv(folder_path)

            print(f"[DEBUG] Latest CSV for {lang}: {latest_file}")
            if not latest_file:
                continue

            df = pd.read_csv(latest_file)
            print(f"[DEBUG] Columns in {lang} file: {df.columns.tolist()}")

            if "Aspect" not in df.columns or "Comment" not in df.columns:
                print(f"[ERROR] Missing columns in {latest_file}")
                continue

            grouped = df.groupby("Aspect")["Comment"].apply(list).reset_index()
            for _, row in grouped.iterrows():
                all_aspects.append({
                    "_id": f"{row['Aspect']} ({lang})",
                    "comments": row["Comment"]
                })

        print(f"[DEBUG] Final data count: {len(all_aspects)}")
        return JSONResponse(content=all_aspects)

    except Exception as e:
        print(f"[ERROR] {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
