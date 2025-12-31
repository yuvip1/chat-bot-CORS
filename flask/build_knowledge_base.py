#build_knowlegde_base.py
import pandas as pd
import re

df = pd.read_csv("raw_website_text.csv")

rows = []

def detect_category(url):
    if "registration" in url:
        return "registration"
    if "subscription" in url:
        return "subscription"
    if "network" in url:
        return "network"
    if "station" in url:
        return "network"
    return "general"

for _, row in df.iterrows():
    category = detect_category(row["url"])

    # Split into sentences
    sentences = re.split(r"\.\s+", row["text"])

    for s in sentences:
        s = s.strip()
        if len(s) < 40:
            continue

        rows.append({
            "category": category,
            "text": s
        })

kb = pd.DataFrame(rows)
kb.to_csv("knowledge_base.csv", index=False)

print(f"✅ knowledge_base.csv created with {len(kb)} entries")
