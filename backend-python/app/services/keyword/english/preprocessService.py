import os
import json
import re
import pandas as pd
import spacy
from collections import Counter
from fastapi import HTTPException
from nltk.util import ngrams
import nltk

# ✅ Download NLTK dependencies if not done already
nltk.download('punkt')
nltk.download('stopwords')

# ✅ Load SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ✅ Define paths
DATA_DIR = os.path.join("data", "keyword", "english")
RAW_SCRAPED_FILE = os.path.join(DATA_DIR, "raw_scraped_content.json")
CLEANED_SCRAPED_FILE = os.path.join(DATA_DIR, "cleaned_scraped_paragraphs.json")
CLEANED_CSV_FILE = os.path.join(DATA_DIR, "cleaned_paragraphs.csv")
TOP_KEYWORDS_FILE = os.path.join(DATA_DIR, "top_keywords.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ✅ Keyword extraction
def extract_keywords_phrases(text_list, top_k=25):
    all_tokens = []
    for text in text_list:
        doc = nlp(text.lower())
        tokens = [token.text for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]
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

# ✅ Paragraph Cleaner Function
def preprocess_text(content_list):
    cleaned_list = []
    seen_sentences = set()

    # Regex patterns
    phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
    url_pattern = r'https?://\S+|www\.\S+|\b\S+\.(?:com|org|net|edu|gov|io|lk)\b'
    address_pattern = r'\bNo\.?\s\d+[A-Za-z]?[,\s]?.*\b'
    date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{1,2}[a-z]*[,\s]*\d{4}\b'
    year_month_pattern = r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}\b'
    time_range_pattern = r'\b\d{1,2}[:.]?\d{2}?\s?(?:am|pm)\s?(?:to|-)\s?\d{1,2}[:.]?\d{2}?\s?(?:am|pm)\b'
    currency_pattern = r'\b(?:LKR|Mn|Rs|USD|EUR|GBP|INR)\b'
    number_pattern = r'\b\d+\b'
    bullet_pattern = r'\b[a-zA-Z]\.\s+'
    meaningless_pattern = r'\b(?:Up to|off on|valid till|discount on|limited time|offer ends)\b.*'
    sinhala_tamil_pattern = r'[\u0D80-\u0DFF\u0B80-\u0BFF]'
    custom_symbols_pattern = r'[^a-zA-Z\s\.\'",]'
    extra_periods = r'\.{2,}'
    isolated_comma_pattern = r'(,\s*,)+'
    trailing_commas = r',\s*$'
    multiple_commas_mid = r'\s*,\s*,\s*'
    isolated_letter_end_pattern = r'\b[a-zA-Z]\b[\s\.]*$'
    dangling_short_word = r'\b\w{1,2}\s*$'

    stop_words = set([
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
        "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was",
        "were", "will", "with", "you","frequently","about","questions", "ear",
        "month","monthly", "privacy","policy"
    ])

    for content in content_list:
        try:
            if isinstance(content, dict) and "sentence" in content:
                content = content["sentence"]
            elif not isinstance(content, str):
                continue

            if re.search(sinhala_tamil_pattern, content):
                continue

            # Cleanup
            cleaned = re.sub(phone_pattern, '', content)
            cleaned = re.sub(url_pattern, '', cleaned)
            cleaned = re.sub(address_pattern, '', cleaned)
            cleaned = re.sub(date_pattern, '', cleaned)
            cleaned = re.sub(year_month_pattern, '', cleaned)
            cleaned = re.sub(time_range_pattern, '', cleaned)
            cleaned = re.sub(currency_pattern, '', cleaned)
            cleaned = re.sub(number_pattern, '', cleaned)
            cleaned = re.sub(bullet_pattern, '', cleaned)
            cleaned = re.sub(meaningless_pattern, '', cleaned)
            cleaned = re.sub(custom_symbols_pattern, ' ', cleaned)

            cleaned = re.sub(isolated_comma_pattern, ' ', cleaned)
            cleaned = re.sub(multiple_commas_mid, ', ', cleaned)
            cleaned = re.sub(trailing_commas, '', cleaned)
            cleaned = re.sub(extra_periods, '.', cleaned)
            cleaned = re.sub(r'\s*\.\s*\.', '.', cleaned)
            cleaned = re.sub(isolated_letter_end_pattern, '', cleaned)
            cleaned = re.sub(dangling_short_word, '', cleaned)

            last_word = cleaned.split()[-1] if cleaned.split() else ''
            if len(last_word) <= 4 and not nlp.vocab[last_word].is_alpha:
                cleaned = ' '.join(cleaned.split()[:-1])

            cleaned = re.sub(r'\b[a-zA-Z]\b[\s\.]*$', '', cleaned).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned.startswith('.'):
                cleaned = cleaned[1:].strip()

            # POS Filtering
            doc = nlp(cleaned)
            tokens = [t.text for t in doc if t.pos_ != "VERB" and t.text.lower() not in stop_words]
            cleaned = ' '.join(tokens).strip()

            if len(cleaned.split()) >= 3 and cleaned not in seen_sentences:
                seen_sentences.add(cleaned)
                cleaned_list.append(cleaned)

        except Exception as e:
            print(f"⚠️ Error cleaning content: {e}")

    if not cleaned_list:
        raise HTTPException(status_code=500, detail="❌ No valid content after preprocessing.")

    return cleaned_list

# ✅ Main Execution
async def preprocess_content():
    try:
        print("🔍 Loading raw scraped content...")
        if not os.path.exists(RAW_SCRAPED_FILE):
            print("❌ Raw scraped content file not found.")
            return False

        with open(RAW_SCRAPED_FILE, "r", encoding="utf-8") as f:
            scraped_content = json.load(f)

        if not isinstance(scraped_content, list) or len(scraped_content) == 0:
            print("❌ Invalid or empty scraped content.")
            return False

        cleaned_content = preprocess_text(scraped_content)
        if not cleaned_content:
            print("❌ No content left after cleaning.")
            return False

        # Save cleaned JSON
        with open(CLEANED_SCRAPED_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_content, f, ensure_ascii=False, indent=2)

        # Save CSV
        df = pd.DataFrame(cleaned_content, columns=["Paragraph"])
        df.to_csv(CLEANED_CSV_FILE, index=False, encoding="utf-8")

        # 🔍 Extract top phrases and save
        keyword_data = extract_keywords_phrases(df["Paragraph"].tolist(), top_k=25)
        with open(TOP_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(keyword_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Successfully cleaned {len(cleaned_content)} paragraphs.")
        print(f"✅ Top keywords & phrases saved to: {TOP_KEYWORDS_FILE}")
        return True

    except json.JSONDecodeError:
        print("❌ JSON decode error.")
        return False
    except Exception as e:
        print(f"❌ Preprocessing error: {e}")
        return False
