import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from datetime import datetime

# --- Setup logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# --- Configuration ---
# CONFIRMED from diagnostic:
#   63 article links per page — href contains "article"
#   Headline text is directly inside the <a> tag
#   Card wrapper: <div class="card border-0">
#   class="sub-title" ×39 per page — headline container

CATEGORIES = {
    "Politics":    "https://www.standardmedia.co.ke/category/3/politics",
    "Business":    "https://www.standardmedia.co.ke/business",
    "Health":      "https://www.standardmedia.co.ke/health",
    "Sports":      "https://www.standardmedia.co.ke/sports",
    "World":       "https://www.standardmedia.co.ke/category/5/world",
    "Counties":    "https://www.standardmedia.co.ke/category/1/counties",
}

MAX_PAGES = 10
MIN_DELAY = 2.0
MAX_DELAY = 4.0
OUTPUT    = "news_raw.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.google.com/",
}


# --- STEP 1: Fetch page ---
def get_soup(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        log.info(f"  HTTP {resp.status_code} | {len(resp.text):,} chars")
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        log.warning(f"  Failed: {e}")
        return None


# --- STEP 2: Parse articles from one page ---
# STRATEGY: find all <a> tags where href contains "article"
# Then keep only anchors that have non-empty text (the headline)
# Duplicates exist because each article has 2 anchors (image + text)
# — we deduplicate by URL at the end

def parse_articles(soup, category_name):
    articles = []

    # Find all article links on the page
    all_links = soup.find_all("a", href=lambda h: h and "/article/" in h)
    log.info(f"  Found {len(all_links)} article links")

    for a in all_links:
        headline = a.get_text(strip=True)

        # Skip anchors with no text (image links)
        if not headline or len(headline) < 10:
            continue

        url = a["href"]

        # Make absolute if relative
        if url.startswith("/"):
            url = "https://www.standardmedia.co.ke" + url

        articles.append({
            "headline":   headline,
            "category":   category_name,
            "url":        url,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    log.info(f"  {len(articles)} headlines with text extracted")
    return articles


# --- STEP 3: Scrape multiple pages per category ---
def scrape_category(category_name, base_url):
    all_articles = []

    for page in range(1, MAX_PAGES + 1):
        url = base_url if page == 1 else f"{base_url}?page={page}"
        log.info(f"\n[{category_name}] Page {page}/{MAX_PAGES} → {url}")

        soup = get_soup(url)
        if soup is None:
            log.warning("  Skipping — fetch failed")
            continue

        page_articles = parse_articles(soup, category_name)

        if not page_articles:
            log.info("  No articles found — stopping this category")
            break

        all_articles.extend(page_articles)
        log.info(f"  Running total [{category_name}]: {len(all_articles)}")

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        log.info(f"  Sleeping {delay:.1f}s...")
        time.sleep(delay)

    return all_articles


# --- STEP 4: Run all categories ---
if __name__ == "__main__":
    print("=" * 60)
    print("  Standard Media Kenya — News Scraper v2")
    print(f"  Categories : {list(CATEGORIES.keys())}")
    print(f"  Max pages  : {MAX_PAGES} per category")
    print(f"  Output     : {OUTPUT}")
    print("=" * 60)

    all_data = []

    for category_name, base_url in CATEGORIES.items():
        articles = scrape_category(category_name, base_url)
        log.info(f"\n[{category_name}] Finished — {len(articles)} articles")
        all_data.extend(articles)

    df = pd.DataFrame(all_data)

    # Deduplicate by URL
    before = len(df)
    df = df.drop_duplicates(subset=["url"])
    log.info(f"\nRemoved {before - len(df)} duplicates")

    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print(f"  ✅  {len(df):,} articles saved → {OUTPUT}")
    print("=" * 60)
    print(f"\n  Shape : {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\n  Articles per category:")
    print(df["category"].value_counts().to_string())
    print(f"\n  Sample headlines:")
    print(df["headline"].head(10).to_string(index=False))
