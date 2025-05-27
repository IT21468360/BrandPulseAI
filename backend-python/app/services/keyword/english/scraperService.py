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

# ✅ WebDriver options
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.fonts": 2
}
options.add_experimental_option("prefs", prefs)

# ✅ Cache setup
CACHE_DIR = "scraped_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_EXPIRATION_MINUTES = 2

# ✅ Constants
MAX_SCROLLS = 10
SCROLL_PAUSE_TIME = 2
MAX_RUNTIME_SECONDS = 60
MAX_INTERNAL_LINKS = 10  # To avoid infinite site crawling

def get_cache_file_path(url):
    hash_name = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hash_name}_cache.json")

def is_cache_valid(cache_file):
    if os.path.exists(cache_file):
        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return (datetime.now() - file_mtime) <= timedelta(minutes=CACHE_EXPIRATION_MINUTES)
    return False

def load_cache(cache_file):
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Cache load error: {e}")
        return None

def save_to_cache(cache_file, data):
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")

def extract_main_text(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Remove unwanted elements
    for tag in soup(['header', 'footer', 'form', 'script', 'style', 'meta', 'noscript']):
        tag.decompose()

    tags_to_extract = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span']
    content_set = set()

    for tag in tags_to_extract:
        elements = soup.find_all(tag)
        for element in elements:
            text = element.get_text(separator=" ", strip=True)
            if text:
                content_set.add(text)

    return list(content_set)

def simulate_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_page(driver, url):
    try:
        driver.get(url)
        simulate_scroll(driver)
        content = extract_main_text(driver)
        return content
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return []

def scrape_website(url):
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)

        scraped_data = []
        visited = set()
        to_visit = [url]

        start_time = time.time()

        while to_visit and len(visited) < MAX_INTERNAL_LINKS:
            current_url = to_visit.pop(0)
            if current_url in visited:
                continue
            print(f"🔗 Scraping: {current_url}")
            visited.add(current_url)

            scraped_data += scrape_page(driver, current_url)

            # Respect time limit
            if time.time() - start_time > MAX_RUNTIME_SECONDS:
                print("⏳ Time limit reached.")
                break

            # Extract internal links (same domain only)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith("/") and len(to_visit) < MAX_INTERNAL_LINKS:
                    full_url = url.rstrip("/") + href
                    if full_url not in visited:
                        to_visit.append(full_url)

    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return None
    finally:
        driver.quit()

    return scraped_data

# ✅ Main scraping function
async def scrape_content(url: str, date_range: dict):
    print(f"🔍 Scraping {url} from {date_range['start']} to {date_range['end']}")

    cache_file = get_cache_file_path(url)
    if is_cache_valid(cache_file):
        os.remove(cache_file)

    scraped_content = scrape_website(url)

    if not scraped_content:
        raise HTTPException(status_code=500, detail="❌ Failed to scrape website.")

    RAW_SCRAPED_FILE = os.path.join("data", "keyword", "english", "raw_scraped_content.json")
    os.makedirs(os.path.dirname(RAW_SCRAPED_FILE), exist_ok=True)

    with open(RAW_SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(scraped_content, f, ensure_ascii=False, indent=2)

    return {"scraped_content": scraped_content}
