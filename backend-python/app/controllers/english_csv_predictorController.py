import os
import re
import pandas as pd
from datetime import datetime
from app.services.sentiment_service import predict_sentiment
from app.db.mongodb import english_collection

def extract_timestamp(filename):
    match = re.search(r"(\d{8}_\d{6})", filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
        except ValueError:
            return datetime.min
    return datetime.min

def get_latest_english_excel():
    folder_path = os.path.join("data", "aspect_classification", "English")
    files = [f for f in os.listdir(folder_path) if f.endswith(".xlsx") and f.startswith("english_aspects_")]

    if not files:
        raise FileNotFoundError("❌ No English Excel (.xlsx) files found!")
    files.sort(key=extract_timestamp, reverse=True)
    latest_file = os.path.join(folder_path, files[0])

    print("🔍 All English XLSX files:", files)
    print("✅ Latest selected English XLSX:", latest_file)
    return latest_file

def process_english_csv_prediction():
    xlsx_path = get_latest_english_excel()
    df = pd.read_excel(xlsx_path)

    if "Comment" not in df.columns or "Aspect" not in df.columns:
        raise ValueError("Excel file must contain 'Comment' and 'Aspect' columns")

    predictions = []
    for _, row in df.iterrows():
        if pd.isna(row["Comment"]) or pd.isna(row["Aspect"]):
            continue
        try:
            sentiment, score = predict_sentiment(row["Comment"], row["Aspect"])
        except Exception as e:
            print(f"❌ Error for comment: {row['Comment']} | Error: {e}")
            continue

        record = {
            "comment": row["Comment"],
            "aspect": row["Aspect"],
            "sentiment_label": sentiment,
            "sentiment_score": score,
            "source_file": os.path.basename(xlsx_path),
            "language": "english"
        }
        if "Date" in df.columns and not pd.isna(row["Date"]):
            record["date"] = row["Date"]
        predictions.append(record)

    inserted = english_collection.insert_many(predictions)
    for i, _id in enumerate(inserted.inserted_ids):
        predictions[i]["_id"] = str(_id)

    return {
        "status": "✅ English Sentiment Saved",
        "total": len(predictions),
        "data": predictions
    }
