import os
import re
import json
import time
import hashlib
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from fastapi import HTTPException

# ✅ WebDriver options (headless mode for efficiency)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")

# ✅ Cache setup
CACHE_DIR = "scraped_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_EXPIRATION_MINUTES = 2

# ✅ Generate a cache file path
def get_cache_file_path(url):
    hash_name = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hash_name}_cache.json")

# ✅ Check cache validity
def is_cache_valid(cache_file):
    if os.path.exists(cache_file):
        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return (datetime.now() - file_mtime) <= timedelta(minutes=CACHE_EXPIRATION_MINUTES)
    return False

# ✅ Load cached data if available
def load_cache(cache_file):
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Cache load error: {e}")
        return None

# ✅ Save scraped content to cache
def save_to_cache(cache_file, data):
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")

# ✅ Extract meaningful text from the webpage
def extract_main_text(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Remove unwanted elements (navigation bars, scripts, etc.)
    for tag in soup(['header', 'footer', 'form', 'a', 'ul', 'li', 'script', 'style', 'meta', 'noscript']):
        tag.decompose()

    # Extract text from relevant tags
    tags_to_extract = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span']
    content_set = set()
    
    for tag in tags_to_extract:
        elements = soup.find_all(tag)
        for element in elements:
            text = element.get_text(separator=" ", strip=True)
            if text:
                content_set.add(text)

    return list(content_set)

# ✅ Scrape content from a given URL
def scrape_website(url, max_pages=3):
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        all_page_content = set()

        for page_num in range(max_pages):
            print(f"🔄 Scraping page {page_num + 1}...")
            page_content = extract_main_text(driver)
            all_page_content.update(page_content)

            try:
                # Try to find a "Next" button or link and click it
                next_buttons = driver.find_elements(By.XPATH, "//a[contains(text(),'Next') or contains(text(),'>>') or contains(text(),'›')]")
                if next_buttons:
                    next_buttons[0].click()
                    time.sleep(3)  # Wait for next page to load
                else:
                    print("ℹ️ No next button found, stopping early.")
                    break
            except Exception as e:
                print(f"⚠️ Pagination error: {e}")
                break

    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return None
    finally:
        driver.quit()

    return list(all_page_content)


# ✅ Main scraping function (called from `scrape_route.py`)
async def scrape_content(url: str, date_range: dict):
    """
    Scrapes the given website URL, caches the results,
    and saves to raw_scraped_content.json.
    """
    print(f"🔍 Scraping {url} from {date_range['start']} to {date_range['end']}")
    
    cache_file = get_cache_file_path(url)
    if is_cache_valid(cache_file):
        os.remove(cache_file)

    scraped_content = scrape_website(url)

    if not scraped_content:
        raise HTTPException(status_code=500, detail="❌ Failed to scrape website.")

    # ✅ Save to RAW_SCRAPED_FILE for downstream preprocessing
    RAW_SCRAPED_FILE = os.path.join("data", "keyword", "sinhala", "raw_scraped_content.json")
    os.makedirs("data", exist_ok=True)
    with open(RAW_SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped_content, f, ensure_ascii=False, indent=2)

    return {"scraped_content": scraped_content}

