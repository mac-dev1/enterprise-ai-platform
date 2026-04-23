# 🤖 Enterprise AI Assistant

An AI-powered internal assistant that answers company-related questions using **Retrieval-Augmented Generation (RAG)** and a **local LLM**.

---

## 🚀 Features

* 📄 Document-based QA (PDF knowledge base)
* 🧠 RAG pipeline (retrieval + grounded generation)
* 💬 Multi-conversation chat (ChatGPT-like UI)
* 🧾 Persistent conversation history (SQLite)
* 🕒 Timestamped messages
* 🔐 User authentication (JWT-based)
* ⚡ Local LLM inference via Ollama (no external API)

---

## 🧠 Architecture

```
Frontend (Vanilla JS)
        ↓
FastAPI (API layer)
        ↓
RAG Pipeline
   ├── Embeddings (Sentence Transformers)
   ├── Vector Search
   └── Context Builder
        ↓
Ollama (LLM - llama3)
        ↓
Response
```

---

## 📂 Project Structure

```
app/
├── api/            # FastAPI routes
├── db/             # Database setup and models
├── models/         # Request/Response models
├── services/       # Business logic
└──  rag/            # RAG pipeline

frontend/
├── index.html
├── styles.css
└── app.js

data/
├── documents/      # Knowledge base (PDFs)
└── index/          # Internal representations of knowledgeq
```

---

## 📦 Setup

```bash
git clone https://github.com/mac-dev1/enterprise-ai-platform.git
cd enterprise-ai-platform
pip install -r requirements.txt
```

---

## ⚙️ Requirements

* Python 3.10+
* Ollama installed

---

## 🧠 Run Ollama

```bash
ollama run llama3
```

(First run will download the model, you can exit ollama after)

---

## ▶️ Run the Application

```bash
python run.py
```

Then wait for "Application startup complete" message and open:

```
http://localhost:8000
```

---

## 🔐 Authentication

* Users must register and login
* JWT token is stored in the browser
* Conversations are linked to each user

---

## 💬 Chat System

* Start a new conversation with **"New Chat"**
* Conversations are saved automatically after the first message
* Sidebar displays conversation history
* Conversations are ordered by most recent activity

---

## 📄 Knowledge Base

Documents are loaded from:

```
data/documents/
```

* Only preloaded documents are used
* Users cannot modify the knowledge base
* PDFs are chunked and embedded at startup

---

## 🧠 RAG Pipeline

1. User sends a question
2. Relevant chunks are retrieved
3. Context is built
4. LLM generates an answer grounded in documents

---

## ⚠️ Limitations

* SQLite does not store timezone information (handled in API layer)
* No streaming responses (yet)

---

## 🚀 Future Improvements

* Real-time streaming responses
* Admin panel (document management)
* Conversation title generation (LLM)
* Role-based permissions
* Advanced retrieval (reranking, hybrid search)

---

## 👨‍💻 Author

Mauricio Casarotto — General Systems Enginner & Mechatronics Engineering student
Interested in Machine Learning, RAG systems, and applied AI

---
