#crawls_website.py
from playwright.sync_api import sync_playwright
import pandas as pd
import time

URLS = [
    "https://cors.surveyofindia.gov.in/registration",
    "https://cors.surveyofindia.gov.in/subscription",
    "https://cors.surveyofindia.gov.in/network",
    "https://cors.surveyofindia.gov.in/stationpoints",
]

rows = []

def extract_text(page):
    selectors = [
        "main",
        "#content",
        ".content",
        "article",
        "section",
        "body"
    ]

    for sel in selectors:
        try:
            if page.locator(sel).count() > 0:
                text = page.inner_text(sel)
                if text and len(text.strip()) > 200:
                    return text
        except:
            pass

    return None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in URLS:
        print("Crawling:", url)
        page.goto(url, timeout=60000)

        # Let JS fully load
        time.sleep(5)

        text = extract_text(page)

        if not text:
            print("⚠️ No usable text from", url)
            continue

        rows.append({
            "url": url,
            "text": text
        })

    browser.close()

df = pd.DataFrame(rows)
df.to_csv("raw_website_text.csv", index=False)

print(f"✅ raw_website_text.csv created with {len(df)} pages")

from append_to_knowledge_base import append_to_kb

new_facts = [
    {
        "category": "subscription",
        "text": "Subscription charges are displayed on the subscription page.",
        "source": "https://cors.surveyofindia.gov.in/subscription"
    },
    {
        "category": "registration",
        "text": "Users must upload required documents during registration.",
        "source": "https://cors.surveyofindia.gov.in/registration"
    }
]

append_to_kb(new_facts)
