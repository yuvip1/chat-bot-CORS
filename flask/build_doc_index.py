#build_doc_index.py
import pandas as pd
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

df = pd.read_csv("knowledge_base.csv")

embeddings = model.encode(
    df["text"].tolist(),
    normalize_embeddings=True
)

joblib.dump(
    {
        "texts": df["text"].tolist(),
        "categories": df["category"].tolist(),
        "embeddings": embeddings,
    },
    "doc_index.pkl"
)

print("✅ Document index built")
