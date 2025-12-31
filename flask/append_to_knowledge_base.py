#appened_to_knoledge_base.py
import pandas as pd
from pathlib import Path

KB_FILE = Path("knowledge_base.csv")

def append_to_kb(new_rows):
    """
    new_rows = list of dicts:
    { category, text, source }
    """

    if KB_FILE.exists():
        df = pd.read_csv(KB_FILE)
    else:
        df = pd.DataFrame(columns=["id", "category", "text", "source"])

    existing_texts = set(df["text"].astype(str))

    clean_rows = []
    for row in new_rows:
        if row["text"] not in existing_texts:
            clean_rows.append(row)

    if not clean_rows:
        print("ℹ️ No new knowledge to add")
        return

    new_df = pd.DataFrame(clean_rows)
    start_id = len(df) + 1
    new_df.insert(0, "id", range(start_id, start_id + len(new_df)))

    final = pd.concat([df, new_df], ignore_index=True)
    final.to_csv(KB_FILE, index=False)

    print(f"✅ Added {len(new_df)} new entries to knowledge_base.csv")
