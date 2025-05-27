import re
import nltk
nltk.download('words')
from langdetect import detect
from nltk.corpus import words as nltk_words

# One-time requirement:
# import nltk; nltk.download('words')

# ✅ Load English words from NLTK
ENGLISH_WORDS = set(nltk_words.words())

# Sinhala and Tamil Unicode detection
SINHALA_UNICODE = re.compile(r'[\u0D80-\u0DFF]')
TAMIL_UNICODE = re.compile(r'[\u0B80-\u0BFF]')

# Singlish & Tanglish keywords
SINGLISH_KEYWORDS = [
    "meke", "eka", "pennuwa", "aiya", "thama", "nathuwa", "hariyata", "ehemai", "ehemay",
    "puluwn", "ganna", "denna", "karanna", "puluwanda", "balanna", "illanawa", "thiyenawa",
    "pennanna", "keyanna", "bala", "giyama", "mage", "oyaa", "mama", "thopi", "adurana",
    "rata", "ayye", "modayo", "hadaganna", "nisa", "payanna", "paththar", "apita", "eka hari", "veida",
    "hithagena", "inney", "enawa", "ennako", "yawanna", "awlak", "thiyenawada", "bari", "pitin", 
    "uththara", "thawa", "pamanak", "bawitha", "uththarayi", "inneyda", "samanya", "pahadili", 
    "widihata", "wela", "yanne", "barida", "hamba", "puluwan", "dila", "gnn", "tikak", "paara", 
    "kaata", "dunnoth", "tiyana", "apahu", "uththare", "karapu", "thiyanawanam", "meken", "Rathnapure",
    "thiyanawanamda", "witarayi", "monawada", "mata", "lebenawada", "kianne", "salli", "krla", "thynna", "baid",
    "mokadda", "danna", "account eka", "mge", "widihk", "awhsya", "smnya", "apit", "igen", "okma", "owa", "okkoma", "puluvn",
    "wlt", "brid", "kiyanne", "mageth", "banku", "bankuwa", "isthuthi", "krnn", "karana", "karanne", "thiynwa", "Me normal account dha?"
]


TANGLISH_KEYWORDS = [
    "illa", "enna", "mudiyala", "pannalama", "irundha", "vanthuten", "kasu", "beta", "banao", "phele", "dekh", "honeka"
    "sollunga", "eppdi", "aalu", "anna", "enakku", "vendum", "nerppurathu", "irikida", "pannurathu", "pannuravangata", "eppedi"
    "kodukanum", "yaruku", "yenga", "Panalama", "panniradhunu", "irukka", "eppidi", "akkalukku", "podunka", "patri", "pannuvathu"
    "poadunga", "vankuran", "enapananum", "pandraanga", "eppadi", "edukkurathu", "ithila", "ethu", "iruku", "puriyamatengudhu",
    "edhunu", "eranthutaru", "edukala", "podunga", "paththi", "ondu", " irku", "cennect", "mudima", "Bhai", "Bhaiya", "jaaega", "pannure",
    "mazagati", "falige", "naber", "yichala"
]

# ✅ Utility to check if comment is mostly English
def is_mostly_english(text, threshold=0.8):
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    if not words:
        return False
    english_count = sum(1 for word in words if word in ENGLISH_WORDS)
    return english_count / len(words) >= threshold

# 🔍 Main language detection function
def detect_language(text):
    try:
        text_lower = text.lower()

        # ✅ Sinhala Unicode or strong Singlish override
        if SINHALA_UNICODE.search(text) or any(word in text_lower for word in SINGLISH_KEYWORDS):
            return "si"

        # ❌ Tamil Unicode or strong Tanglish override
        if TAMIL_UNICODE.search(text) or any(word in text_lower for word in TANGLISH_KEYWORDS):
            return "ta"

        # 🌍 Fallback to langdetect
        lang = detect(text)

        # ✅ Word-ratio override
        if is_mostly_english(text):
            return "en"

        return lang if lang in ["en", "si", "ta"] else "other"

    except:
        return "other"
