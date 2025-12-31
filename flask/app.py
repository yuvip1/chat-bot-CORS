from flask import Flask
from flask_socketio import SocketIO, emit
from pathlib import Path
from datetime import datetime
import csv
import joblib
import numpy as np
import re
import requests
from sentence_transformers import SentenceTransformer
from live_crawls import hybrid_live_crawl

print("🔥 CHATBOT RUNNING (FINAL STABLE VERSION) 🔥")

# ==================================================
# Configuration
# ==================================================

OLLAMA_MODEL = "phi3:mini"
OLLAMA_URL = "http://localhost:11434/api/generate"

SIMILARITY_THRESHOLD = 0.35
TOP_K = 5

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

CHAT_LOG = LOG_DIR / "chat_logs.csv"
USER_FILE = LOG_DIR / "user_detail.csv"

URL_REGEX = re.compile(r"https?://\S+")
REGION_REGEX = re.compile(r"region\s*(\d+)", re.IGNORECASE)
PLAN_REGEX = re.compile(r"\b(plan|plans|pricing|charges|subscription)\b", re.IGNORECASE)

# ==================================================
# Load Models / Index
# ==================================================

embedder = SentenceTransformer("all-MiniLM-L6-v2")
doc_index = joblib.load(BASE_DIR / "doc_index.pkl")

texts = doc_index["texts"]
categories = doc_index["categories"]
embeddings = doc_index["embeddings"]

# ==================================================
# Utility Functions
# ==================================================

def log_chat(text):
    file_exists = CHAT_LOG.exists()
    with CHAT_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "text"])
        writer.writerow([datetime.now().isoformat(), text])


def retrieve_top_docs(query, top_k=TOP_K):
    q_vec = embedder.encode([query], normalize_embeddings=True)[0]
    scores = np.dot(embeddings, q_vec)
    top_idx = scores.argsort()[-top_k:][::-1]

    results = []
    for i in top_idx:
        results.append({
            "text": texts[i],
            "category": categories[i],
            "score": float(scores[i])
        })
    return results


def infer_allowed_categories(query):
    q = query.lower()

    if any(k in q for k in ["service", "offer", "subscription"]):
        return ["subscription"]

    if any(k in q for k in ["register", "registration", "sign up"]):
        return ["registration"]

    if any(k in q for k in ["network", "ip", "port", "mount"]):
        return ["network"]

    return None


def clean_retrieved(results):
    """
    LIGHT filtering only.
    Do NOT remove valid factual answers.
    """
    clean = []

    for r in results:
        text = r["text"].strip().lower()

        # Remove only real questions
        if text.endswith("?"):
            continue

        # Remove UI junk
        if "skip main content" in text or "welcome to" in text:
            continue

        clean.append(r)

    return clean


def extract_region_url(text, query):
    match = REGION_REGEX.search(query)
    if not match:
        return None

    urls = URL_REGEX.findall(text)
    return urls[0] if urls else None


def get_all_subscription_plans():

    plans = []
    for text, cat in zip(texts, categories):
        if cat == "subscription" and text.lower().startswith("plan"):
            plans.append(text.strip())
    return plans


def format_plans_as_steps(plans):
    return "\n".join(f"{i+1}. {plan}" for i, plan in enumerate(plans))


def to_steps(text):
    parts = [p.strip().capitalize() for p in text.split(",") if p.strip()]
    return "\n".join(f"{i+1}. {p}" for i, p in enumerate(parts))


def ollama_short_steps(query, fact):
    prompt = f"""
Answer the question in SHORT NUMBERED STEPS.
Use ONLY the information below.
Do NOT add new information.

FACT:
{fact}

QUESTION:
{query}

ANSWER:
""".strip()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 80}
            },
            timeout=40
        )
        return r.json().get("response", "").strip()

    except Exception:
        return "I do not have that information."

# ==================================================
# Flask + Socket.IO
# ==================================================

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on("connect")
def connect():
    emit("bot_reply", {
        "text": "👋 Hi! How can I help you?",
        "intent": "system",
        "confidence": "1.00"
    })


@socketio.on("message")
def handle_message(data):
    query = data.get("text", "").strip()
    if not query:
        return

    # -------------------------------
    # Subscription plans shortcut
    # -------------------------------
    if PLAN_REGEX.search(query):
        plans = get_all_subscription_plans()
        reply = format_plans_as_steps(plans) if plans else "I do not have subscription plan details."

        emit("bot_reply", {
            "text": "ANSWER:\n" + reply,
            "intent": "rag",
            "confidence": "OK"
        })
        log_chat(query)
        return

    # -------------------------------
    # Normal RAG flow
    # -------------------------------
    candidates = retrieve_top_docs(query)
    best_score = candidates[0]["score"]

    if best_score >= SIMILARITY_THRESHOLD:
        allowed = infer_allowed_categories(query)
        if allowed:
            candidates = [c for c in candidates if c["category"] in allowed]

        candidates = clean_retrieved(candidates)

        if not candidates:
            reply = "I do not have that information."
        else:
            fact = candidates[0]["text"]

            # Region URL shortcut
            region_url = extract_region_url(fact, query)
            urls = URL_REGEX.findall(fact)

           # Always handle deterministic government facts without LLM
        if candidates[0]["category"] in ["registration", "network", "subscription"]:
            reply = to_steps(fact)

# URLs / region links
        elif region_url:
            reply = region_url
        elif urls:
            reply = urls[0]

# Only descriptive text goes to LLM
        else:
            reply = ollama_short_steps(query, fact)


    # -------------------------------
    # Hybrid crawl fallback
    # -------------------------------
    else:
        live = hybrid_live_crawl(query)
        reply = ollama_short_steps(query, live) if live else "I do not have that information."

    emit("bot_reply", {
        "text": "ANSWER:\n" + reply,
        "intent": "rag",
        "confidence": f"{best_score:.2f}"
    })

    log_chat(query)


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
