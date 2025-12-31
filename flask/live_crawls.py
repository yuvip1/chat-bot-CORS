# live_crawl.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re


# --------------------------------------------------
# Allowed pages only (VERY IMPORTANT for safety)
# --------------------------------------------------

ALLOWED_URLS = {
    "registration": "https://cors.surveyofindia.gov.in/registration",
    "subscription": "https://cors.surveyofindia.gov.in/subscription",
    "network": "https://cors.surveyofindia.gov.in/network",
    "stationpoints": "https://cors.surveyofindia.gov.in/stationpoints",
}


# --------------------------------------------------
# Infer which page to crawl from user query
# --------------------------------------------------

def infer_page_from_query(query: str):
    q = query.lower()

    if any(k in q for k in ["register", "registration", "sign up"]):
        return ALLOWED_URLS["registration"]

    if any(k in q for k in ["subscription", "plan", "price", "charge", "cost"]):
        return ALLOWED_URLS["subscription"]

    if any(k in q for k in ["network", "ip", "port", "mount"]):
        return ALLOWED_URLS["network"]

    if any(k in q for k in ["station", "map", "station point"]):
        return ALLOWED_URLS["stationpoints"]

    return None


# --------------------------------------------------
# Clean extracted text
# --------------------------------------------------

def clean_text(raw_text: str) -> str:
    """
    Cleans webpage text:
    - Removes very short lines
    - Removes junk
    - Limits size
    """

    lines = raw_text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()
        if len(line) < 30:
            continue
        if "copyright" in line.lower():
            continue
        clean_lines.append(line)

    # Limit output to avoid huge prompts
    return "\n".join(clean_lines[:40])


# --------------------------------------------------
# Crawl a single page safely
# --------------------------------------------------

def crawl_page(url: str) -> str:
    """
    Safely crawl a single whitelisted page and extract visible text.
    """

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_timeout(4000)  # allow JS rendering

            raw_text = page.inner_text("body")

            browser.close()

            return clean_text(raw_text)

    except PlaywrightTimeoutError:
        print(f"⚠️ Timeout while crawling {url}")
        return ""

    except Exception as e:
        print(f"⚠️ Crawl error for {url}: {e}")
        return ""


# --------------------------------------------------
# Main hybrid crawl entry
# --------------------------------------------------

def hybrid_live_crawl(query: str) -> str:
    """
    High-level function:
    - Infers page from query
    - Crawls only that page
    - Returns cleaned text
    """

    url = infer_page_from_query(query)
    if not url:
        return ""

    print(f"🌐 Live crawling: {url}")
    return crawl_page(url)
