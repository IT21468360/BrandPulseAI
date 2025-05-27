import os
import re
import json
import torch
import pandas as pd
from datetime import datetime
from torch.nn.functional import softmax
from pymongo import MongoClient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.utils.language_identifier import detect_language
from app.controllers.english_aspect_predict_controller import garbage_then_aspect as english_combined_predict
from app.controllers.sinhala_aspect_predict_controller import is_sinhala_garbage, aspect_tokenizer, aspect_model, aspect_label_map, aspect_lexicon

print('first step done')
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME", "BrandPulseAI")]

print("🔍 Connected to DB:", db.name)
print("🔍 Mongo URI =", os.getenv("MONGODB_URI"))

API_KEYS = ['AIzaSyCqySWOBgkTOJNF4kmAHv5Wpa9lP25a3B4']
MAX_RESULTS = 100

def get_api_key(index):
    return API_KEYS[index % len(API_KEYS)]

def get_latest_keywords_from_mongo():
    try:
        record = db["saved_combinations"].find_one(
            sort=[("created_at", -1), ("_id", -1)]
        )
        if record and 'keywords' in record and 'brand' in record:
            print(f"✅ Fetched brand: {record['brand']}, keywords: {record['keywords']} from saved_combinations")
            return record['keywords'], record['brand']
        else:
            raise ValueError("❌ No valid keywords or brand found in saved_combinations.")
    except Exception as e:
        print(f"MongoDB error: {e}")
        return [], None

def remove_emojis(text):
    emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F'
                               r'\U0001F300-\U0001F5FF'
                               r'\U0001F680-\U0001F6FF'
                               r'\U0001F1E0-\U0001F1FF'
                               r'\U00002700-\U000027BF'
                               r'\U000024C2-\U0001F251]', flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def search_youtube(keywords, api_key_index):
    youtube = build("youtube", "v3", developerKey=get_api_key(api_key_index))
    videos = []
    query_string = " | ".join(keywords[:5])

    response = youtube.search().list(
        q=query_string,
        part='id,snippet',
        maxResults=MAX_RESULTS,
        type='video'
    ).execute()

    for item in response.get('items', []):
        if 'videoId' not in item.get('id', {}):
            print("⚠️ Skipping invalid item (no videoId):", item)
            continue  # Skip non-video results like channels or playlists

        video_id = item['id']['videoId']
        snippet = item['snippet']
        title = snippet.get('title', '')
        description = snippet.get('description', '')
        combined_text = f"{title} {description}".lower()

        matched_keywords = [kw.lower() for kw in keywords if kw.lower() in combined_text]

        if len(matched_keywords) / len(keywords) >= 0.3:
            video_info = youtube.videos().list(part="statistics,snippet", id=video_id).execute()
            stats = video_info['items'][0]['statistics']
            full_snippet = video_info['items'][0]['snippet']
            description_text = full_snippet.get('description', '')

            videos.append({
                'video_id': video_id,
                'title': full_snippet.get('title', ''),
                'description': description_text,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'likes': stats.get('likeCount', 'N/A'),
                'views': stats.get('viewCount', 'N/A'),
                'comment_count': stats.get('commentCount', 'N/A'),
                'published_at': full_snippet.get('publishedAt', 'N/A'),
                'hashtags': ", ".join(re.findall(r"#\S+", description_text)),
                'keyword_hits': len(matched_keywords)
            })

    return videos

def get_top_comments(video_id, api_key_index, max_comments=200):
    youtube = build("youtube", "v3", developerKey=get_api_key(api_key_index))
    comments = []
    next_page_token = None
    while len(comments) < max_comments:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                textFormat="plainText",
                pageToken=next_page_token
            ).execute()
            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    'comment': snippet["textDisplay"],
                    'author': snippet["authorDisplayName"],
                    'like_count': snippet.get("likeCount", 0),
                    'published_at': snippet.get("publishedAt", "N/A")
                })
                if len(comments) >= max_comments:
                    break
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        except HttpError:
            return "error"
    return comments

def classify_comment(text, lexicon, processed_comments):
    clean_text = remove_emojis(text).strip().lower()
    if not clean_text or clean_text in processed_comments:
        return None, None

    lang = detect_language(clean_text)

    if lang == "en":
        result = english_combined_predict(clean_text)
        if result["label"] == "valid":
            return result, "en"
        if any(phrase in clean_text for phrase in ["can i use", "best app", "how to use"]):
            return {"label": "valid", "aspect": "Digital Banking Experience"}, "en"
        return result, "en"

    elif lang == "si":
        if is_sinhala_garbage(clean_text):
            return {"label": "garbage", "aspect": None}, "si"

        inputs = aspect_tokenizer(clean_text, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = aspect_model(**inputs)
            probs = softmax(outputs.logits, dim=1).squeeze()

        model_scores = {aspect_label_map[i]: probs[i].item() for i in range(len(aspect_label_map))}
        lexicon_scores = {aspect: 0 for aspect in aspect_label_map.values()}

        for aspect, keywords in aspect_lexicon.items():
            for kw in keywords:
                if kw.lower() in clean_text:
                    lexicon_scores[aspect] += 1

        max_lex = max(lexicon_scores.values()) or 1
        lexicon_scores = {k: v / max_lex for k, v in lexicon_scores.items()}

        combined_scores = {
            aspect: 0.7 * model_scores.get(aspect, 0) + 0.3 * lexicon_scores.get(aspect, 0)
            for aspect in aspect_label_map.values()
        }

        final_aspect = max(combined_scores, key=combined_scores.get)

        if model_scores.get(final_aspect, 0) < 0.4 and lexicon_scores.get(final_aspect, 0) < 0.1:
            final_aspect = "Others"

        return {
            "label": "valid",
            "aspect": final_aspect,
            "model_score": model_scores.get(final_aspect, 0),
            "lexicon_score": lexicon_scores.get(final_aspect, 0),
            "final_score": combined_scores.get(final_aspect, 0)
        }, "si"

    else:
        return {"label": "skip", "aspect": None}, lang

def scrape_and_classify_to_mongo_and_csv(start_date: str, end_date: str):
    try:
        keywords, brand = get_latest_keywords_from_mongo()
        if not keywords or not brand:
            return {"status": "error", "message": "No keywords or brand found in MongoDB"}

        scrape_id = datetime.utcnow().isoformat()
        print("\n📦 Scraping started for:", brand, keywords, scrape_id)

        api_key_index = 0
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        results = {
            "english_valid": [], "sinhala_valid": [],
            "english_garbage": [], "sinhala_garbage": [],
            "skipped_langs": {}
        }

        processed_comments = set()

        for video in search_youtube(keywords, api_key_index):
            comments = get_top_comments(video['video_id'], api_key_index)
            if comments == "error":
                continue

            for c in comments:
                try:
                    comment_date = datetime.strptime(c['published_at'], "%Y-%m-%dT%H:%M:%SZ")
                except:
                    continue
                if not (start_dt <= comment_date <= end_dt):
                    continue

                cleaned_comment = remove_emojis(c['comment']).encode('utf-8', 'ignore').decode('utf-8', 'ignore')

                result, lang = classify_comment(c['comment'], None, processed_comments)
                if not result or result["label"] == "skip":
                    results["skipped_langs"][lang] = results["skipped_langs"].get(lang, 0) + 1
                    continue

                record = {
                    "comment": cleaned_comment,
                    "aspect": result.get("aspect"),
                    "published_at": c['published_at'],
                    "brand": brand,
                    "trigger_keywords": keywords,
                    "scrape_id": scrape_id
                }

                if lang == "si" and result["label"] == "valid":
                    record.update({
                        "model_score": result.get("model_score"),
                        "lexicon_score": result.get("lexicon_score"),
                        "final_score": result.get("final_score")
                    })

                if result["label"] == "valid":
                    results["english_valid" if lang == "en" else "sinhala_valid"].append(record)
                else:
                    results["english_garbage" if lang == "en" else "sinhala_garbage"].append(record)

        if results["english_valid"]:
            db["English_Aspects"].insert_many(results["english_valid"])
        if results["sinhala_valid"]:
            db["Sinhala_Aspects"].insert_many(results["sinhala_valid"])
        if results["english_garbage"]:
            db["English_Garbage"].insert_many(results["english_garbage"])
        if results["sinhala_garbage"]:
            db["Sinhala_Garbage"].insert_many(results["sinhala_garbage"])

        print("🧠 Returned scrape_id to frontend:", scrape_id)

        # ✅ Save to XLSX
        scrape_suffix = datetime.strptime(scrape_id, "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y%m%d_%H%M%S")

        


        # ✅ Get the root path of backend-python/
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


        # ✅ Set correct save path to backend-python/data
        base_path = os.path.join(BASE_DIR, "data")

        # ✅ Aspect & Garbage paths
        aspect_path_si = os.path.join(base_path, "aspect_classification", "Sinhala")
        aspect_path_en = os.path.join(base_path, "aspect_classification", "English")
        garbage_path_si = os.path.join(base_path, "garbage_classification", "Sinhala")
        garbage_path_en = os.path.join(base_path, "garbage_classification", "English")

        # ✅ Create folders if not exist
        os.makedirs(aspect_path_si, exist_ok=True)
        os.makedirs(aspect_path_en, exist_ok=True)
        os.makedirs(garbage_path_si, exist_ok=True)
        os.makedirs(garbage_path_en, exist_ok=True)


        # 🔄 Save Sinhala Aspect Data
        if results["sinhala_valid"]:
            df_si_aspect = pd.DataFrame(results["sinhala_valid"])[["comment", "aspect", "published_at"]]
            df_si_aspect.columns = ["Comment", "Aspect", "Date"]

            path = os.path.join(aspect_path_si, f"sinhala_aspects_{scrape_suffix}.xlsx")
            df_si_aspect.to_excel(path, index=False)
            print(f"✅ Saved Sinhala aspect data → {path}")

        # 🔄 Save English Aspect Data
        if results["english_valid"]:
            df_en_aspect = pd.DataFrame(results["english_valid"])[["comment", "aspect", "published_at"]]
            df_en_aspect.columns = ["Comment", "Aspect", "Date"]
            path = os.path.join(aspect_path_en, f"english_aspects_{scrape_suffix}.xlsx")
            df_en_aspect.to_excel(path, index=False)
            print(f"✅ Saved English aspect data → {path}")

        # 🗑️ Save Sinhala Garbage
        if results["sinhala_garbage"]:
            df_si_garbage = pd.DataFrame(results["sinhala_garbage"])[["comment", "published_at"]]
            path = os.path.join(garbage_path_si, f"sinhala_garbage_{scrape_suffix}.xlsx")
            df_si_garbage.to_excel(path, index=False)
            print(f"✅ Saved Sinhala garbage data → {path}")

        # 🗑️ Save English Garbage
        if results["english_garbage"]:
            df_en_garbage = pd.DataFrame(results["english_garbage"])[["comment", "published_at"]]
            path = os.path.join(garbage_path_en, f"english_garbage_{scrape_suffix}.xlsx")
            df_en_garbage.to_excel(path, index=False)
            print(f"✅ Saved English garbage data → {path}")

        print("📁 Current Working Directory:", os.getcwd())

        print("📁 BASE_DIR =", BASE_DIR)
        print("📁 Data Save Base Path =", base_path)


        return {
            "status": "success",
            "brand": brand,
            "keywords": keywords,
            "scrape_id": scrape_id,
            "english_aspects": len(results["english_valid"]),
            "sinhala_aspects": len(results["sinhala_valid"]),
            "english_garbage": len(results["english_garbage"]),
            "sinhala_garbage": len(results["sinhala_garbage"]),
            "skipped_languages": results["skipped_langs"]
        }

    except Exception as e:
        print("🔥 ERROR during scrape_and_classify:", str(e))
        return {"status": "error", "message": str(e)}
