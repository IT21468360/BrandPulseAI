import os
import re
import pandas as pd
from datetime import datetime
from app.services.sentiment_sinhala_service import predict_sentiment_sinhala
from app.db.mongodb import sinhala_collection
from datetime import datetime
import pytz

def extract_timestamp(filename):
    match = re.search(r"(\d{8}_\d{6})", filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
        except ValueError:
            return datetime.min
    return datetime.min

def get_latest_sinhala_excel():
    folder_path = os.path.join("data", "aspect_classification", "Sinhala")
    files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx") and f.startswith("sinhala_aspects_")]

    if not files:
        raise FileNotFoundError("❌ No Sinhala Excel (.xlsx) files found!")
    files.sort(key=extract_timestamp, reverse=True)
    latest_file = os.path.join(folder_path, files[0])

    print("🔍 All Sinhala XLSX files:", files)
    print("✅ Latest selected Sinhala XLSX:", latest_file)
    return latest_file

def process_sinhala_csv_prediction():
    xlsx_path = get_latest_sinhala_excel()
    df = pd.read_excel(xlsx_path)  # ✅ Automatically handles Unicode/Sinhala

    if "Comment" not in df.columns or "Aspect" not in df.columns:
        raise ValueError("Excel file must contain 'Comment' and 'Aspect' columns")

    predictions = []
    for _, row in df.iterrows():
        if pd.isna(row["Comment"]) or pd.isna(row["Aspect"]):
            continue
        try:
            sentiment, score = predict_sentiment_sinhala(row["Comment"], row["Aspect"])
        except Exception as e:
            print(f"❌ Error for comment: {row['Comment']} | Error: {e}")
            continue
        sri_lanka_time = datetime.now(pytz.timezone("Asia/Colombo"))
        record = {
            "comment": row["Comment"],
            "aspect": row["Aspect"],
            "sentiment_label": sentiment,
            "sentiment_score": score,
            "source_file": os.path.basename(xlsx_path),
            "language": "sinhala",
            "created_at": sri_lanka_time
        }
        if "Date" in df.columns and not pd.isna(row["Date"]):
            record["date"] = row["Date"]
        predictions.append(record)

    inserted = sinhala_collection.insert_many(predictions)
    for i, _id in enumerate(inserted.inserted_ids):
        predictions[i]["_id"] = str(_id)

    return {
        "status": "✅ Sinhala Sentiment Saved",
        "total": len(predictions),
        "data": predictions
    }