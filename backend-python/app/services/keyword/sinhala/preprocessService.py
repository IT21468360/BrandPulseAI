import os
import json
import re
import pandas as pd
from collections import Counter
from fastapi import HTTPException
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords

# 🔁 Download resources
nltk.download('punkt')
nltk.download('stopwords')

# ✅ Define paths
DATA_DIR = os.path.join("data", "keyword", "sinhala")
RAW_SCRAPED_FILE = os.path.join(DATA_DIR, "raw_scraped_content.json")
CLEANED_SCRAPED_FILE = os.path.join(DATA_DIR, "cleaned_scraped_paragraphs.json")
CLEANED_CSV_FILE = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
TOP_KEYWORDS_FILE = os.path.join(DATA_DIR, "top_keywords.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Special Sinhala ZWJ words
SPECIAL_SINHALA_WORDS = [
    "ශ්‍රී", "ශ්‍රීමත්", "විශ්වවිද්‍යාලය", "ශ්‍රී ලංකා", "ශ්‍රී ජයවර්ධනපුර", "කළමනාකරණ",
    "ගණකාධිකරණය", "අධ්‍යක්ෂ", "ප්‍රධාන", "සභාපති"
]
special_sinhala_pattern = re.compile(r'(?:' + '|'.join(re.escape(word) for word in SPECIAL_SINHALA_WORDS) + r')')

# ✅ Sinhala Cleaning Function
def clean_sinhala_content(content_list):
    cleaned_list = []
    seen_sentences = set()

    phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
    url_pattern = r'https?://\S+|www\.\S+|\b\S+\.(?:com|org|net|edu|gov|io|lk)\b'
    address_pattern = r'\bNo\.?\s\d+[A-Za-z]?[,\s]?.*\b'
    full_date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{1,2}[a-z]*[,\s]*\d{4}\b'
    time_range_pattern = r'\b\d{1,2}[:.]?\d{2}?\s?(?:am|pm)\s?(?:to|-)\s?\d{1,2}[:.]?\d{2}?\s?(?:am|pm)\b'
    number_pattern = r'\b\d+\b'
    redundant_period_pattern = r'(?<=\.)\s*\.(?:\s*\.)*'
    bullet_pattern = r'(?:\u2022|\u25E6|\u2023|\*)\s?'
    meaningless_sentence_pattern = r'\b(?:Up to|off on|valid till|discount on|limited time|offer ends)\b.*'
    currency_pattern = r'\b(?:LKR|Mn|Rs|USD|EUR|GBP|INR)\b'
    english_word_pattern = r'\b[A-Za-z]+\b'
    all_symbols_pattern = r'[^\u0D80-\u0DFF\s\u200D]'

    for content in content_list:
        try:
            if isinstance(content, dict) and "sentence" in content:
                content = content["sentence"]
            elif not isinstance(content, str):
                continue

            cleaned_content = re.sub(phone_pattern, '', content)
            cleaned_content = re.sub(url_pattern, '', cleaned_content)
            cleaned_content = re.sub(address_pattern, '', cleaned_content)
            cleaned_content = re.sub(full_date_pattern, '', cleaned_content)
            cleaned_content = re.sub(time_range_pattern, '', cleaned_content)
            cleaned_content = re.sub(number_pattern, '', cleaned_content)
            cleaned_content = re.sub(redundant_period_pattern, '', cleaned_content)
            cleaned_content = re.sub(bullet_pattern, '', cleaned_content)
            cleaned_content = re.sub(meaningless_sentence_pattern, '', cleaned_content)
            cleaned_content = re.sub(currency_pattern, '', cleaned_content)
            cleaned_content = re.sub(english_word_pattern, '', cleaned_content)
            cleaned_content = re.sub(all_symbols_pattern, ' ', cleaned_content)

            cleaned_content = ' '.join(cleaned_content.split())

            if cleaned_content and cleaned_content not in seen_sentences:
                seen_sentences.add(cleaned_content)
                cleaned_list.append(cleaned_content)
        except Exception as e:
            print(f"⚠️ Error cleaning Sinhala content: {e}")

    if not cleaned_list:
        raise HTTPException(status_code=500, detail="❌ No valid Sinhala content after preprocessing.")

    return cleaned_list

# ✅ Extract most frequent words and phrases
def extract_keywords_phrases(text_list, top_k=25):
    all_tokens = []
    for text in text_list:
        tokens = nltk.word_tokenize(text)
        tokens = [token for token in tokens if re.match(r'^[\u0D80-\u0DFF\u200D]+$', token)]  # Sinhala-only
        all_tokens.extend(tokens)

    unigram_counts = Counter(all_tokens)
    bigram_counts = Counter(ngrams(all_tokens, 2))
    trigram_counts = Counter(ngrams(all_tokens, 3))

    top_unigrams = unigram_counts.most_common(top_k)
    top_bigrams = [(" ".join(bi), count) for bi, count in bigram_counts.most_common(top_k)]
    top_trigrams = [(" ".join(tri), count) for tri, count in trigram_counts.most_common(top_k)]

    return {
        "top_unigrams": top_unigrams,
        "top_bigrams": top_bigrams,
        "top_trigrams": top_trigrams
    }

# ✅ Main execution function
async def preprocess_content():
    try:
        print("🔍 Loading raw Sinhala scraped content...")
        if not os.path.exists(RAW_SCRAPED_FILE):
            print("❌ Sinhala raw scraped content file not found.")
            return False

        with open(RAW_SCRAPED_FILE, "r", encoding="utf-8") as f:
            scraped_content = json.load(f)

        if not isinstance(scraped_content, list) or len(scraped_content) == 0:
            print("❌ Invalid or empty Sinhala scraped content.")
            return False

        cleaned_content = clean_sinhala_content(scraped_content)
        if not cleaned_content:
            print("❌ No Sinhala content left after cleaning.")
            return False

        # Save cleaned JSON
        with open(CLEANED_SCRAPED_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_content, f, ensure_ascii=False, indent=2)

        # Save CSV
        df = pd.DataFrame(cleaned_content, columns=["Paragraph"])
        df_filtered = df[df["Paragraph"].apply(lambda x: len(x.split()) > 2)]
        df_filtered.to_csv(CLEANED_CSV_FILE, index=False, encoding="utf-8")

        # 🔍 Extract and save frequent keywords/phrases
        keyword_results = extract_keywords_phrases(df_filtered["Paragraph"].tolist(), top_k=25)
        with open(TOP_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(keyword_results, f, ensure_ascii=False, indent=2)

        print(f"✅ Cleaned {len(df_filtered)} Sinhala paragraphs.")
        print(f"✅ Top keywords & phrases saved to: {TOP_KEYWORDS_FILE}")
        return True

    except json.JSONDecodeError:
        print("❌ JSON decode error.")
        return False
    except Exception as e:
        print(f"❌ Sinhala preprocessing error: {e}")
        return False
