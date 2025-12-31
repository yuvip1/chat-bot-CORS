1. Introduction

The system follows a Hybrid Retrieval-Augmented Generation (RAG) architecture, combining:

A preprocessed knowledge base for fast and reliable answers

Live website crawling as a fallback when information is not available locally

This approach ensures that the chatbot remains scalable, accurate, and up-to-date without relying solely on live website analysis.


2. System Architecture

The chatbot is divided into three major layers:

2.1 Frontend Layer
Built using React.js
Provides a floating chatbot widget with onboarding flow
Collects optional user details (name, phone, email)
Communicates with backend using WebSockets (Socket.IO)

2.2 Backend Layer
Developed using Flask and Flask-SocketIO
Handles:
    User queries
    Knowledge retrieval
    Live crawling fallback
    Response formatting
    User data logging

2.3 AI & Knowledge Layer
Uses Sentence Transformers to convert queries into embeddings
Compares queries with a pre-indexed knowledge base
Uses Ollama (phi3:mini) for:
    Summarization
    Step-based answers
    Controlled language generation


3. Working Methodology

Step 1: User Onboarding
Users optionally enter their name, phone number, and email.
Data is validated on the frontend.
Details are stored in user_detail.csv on the backend.

Step 2: Query Embedding
User query is converted into a vector using SentenceTransformer.
The vector is compared against precomputed embeddings stored in doc_index.pkl.

Step 3: Knowledge Base Retrieval
If similarity score exceeds a defined threshold:
Relevant content is retrieved from knowledge_base.csv
Responses are converted into short, numbered steps
URLs and region-specific information are extracted when applicable

Step 4: Hybrid Live Crawling (Fallback)-
If similarity score is below threshold:
    The system performs live crawling of the official CORS website
    Extracted text is cleaned and summarized using Ollama
If no relevant data is found:
    I do not have that information.

Step 5: Response Delivery
The final response is sent to the frontend in real time via Socket.IO
User queries are logged for analysis and improvement


4. Technologies Used

# Core Backend
Flask>=2.0.1
Flask-SocketIO>=5.3.0
Werkzeug>=2.0.1
python-dotenv>=0.19.0
click>=8.0.1
itsdangerous>=2.0.1
Jinja2>=3.0.3
MarkupSafe>=2.0.1

The commands in the prompt to install the models
pip install Flask
pip install Flask-SocketIO
pip install Werkzeug
pip install python-dotenv
pip install click
pip install itsdangerous
pip install Jinja2
pip install MarkupSafe

# Networking / HTTP
requests>=2.26.0
Command: pip install requests

# AI / NLP / Embeddings
sentence-transformers>=2.2.2
torch>=1.12.0
numpy>=1.21.0
scikit-learn>=1.0.2
joblib>=1.1.0

Commands used: 
pip install sentence-transformers
pip install torch
pip install numpy
pip install scikit-learn
pip install joblib

# Web Crawling / Parsing
beautifulsoup4>=4.10.0
lxml>=4.9.0

Commands:
pip install beautifulsoup4
pip install lxml
pip install trafilatura

# Data Handling
pandas>=1.3.0
Command: pip install pandas

# Optional / Development
pytest>=6.2.5
Command: pip install pytest

# Ollama install
Download from: 
https://ollama.com

Pull the required model from:
ollama pull phi3:mini

Start Ollama server:
ollama serve


