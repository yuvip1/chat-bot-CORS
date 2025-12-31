# backend/build_neural_intent_index.py
import pandas as pd
import joblib
from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading training data...")
df = pd.read_csv("training_data.csv")

texts = df["text"].astype(str).tolist()
intents = df["intent"].tolist()

print("Loading local sentence transformer...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Encoding training examples...")
embeddings = model.encode(texts, normalize_embeddings=True)

joblib.dump(
    {
        "embeddings": embeddings,
        "intents": intents,
        "texts": texts
    },
    "neural_intent_index.pkl"
)

print("✅ Neural intent index created")
