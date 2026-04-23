import sys

from torch import embedding
from app.rag.index_builder import EMB_PATH
from app.services.agent_service import decide_action
from app.services.llm_service import query_llm
import faiss
import numpy as np
import ollama
import os
import pickle
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from datetime import datetime

CHUNKS_PATH = "data/index/chunks.pkl"
EMB_PATH = "data/index/embeddings.pkl"
INDEX = None
ENCODED_CHUNKS = None
# Load model once (important for performance)
model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

def load_index():
    if not os.path.exists(CHUNKS_PATH) or not os.path.exists(EMB_PATH):
        print("No chunks or embbedings loaded")
        print("Load some guide files in the data/documents folder")
        sys.exit()

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    with open(EMB_PATH, "rb") as f:
        embeddings = pickle.load(f)

    INDEX = chunks, embeddings
    ENCODED_CHUNKS = model.encode([c["text"] for c in chunks])
    return INDEX


def retrieve_context(question, stored_chunks, k=5):
    texts = [c["text"] for c in stored_chunks]

    # embeddings
    query_vec = model.encode([question])
    chunk_vecs = ENCODED_CHUNKS #model.encode(texts)

    # similitud coseno
    similarities = cosine_similarity(query_vec, chunk_vecs)[0]

    # ordenar por relevancia
    ranked_indices = similarities.argsort()[::-1]

    # tomar top-k
    results = [stored_chunks[i] for i in ranked_indices[:k]]

    return results

def clean_text(text):
    # eliminar saltos de línea
    text = text.replace("\n", " ")

    # eliminar múltiples espacios
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def build_context(context_chunks, max_chars=1500):
    context = ""
    
    for c in context_chunks:
        #if len(context) + len(c["text"]) < max_chars:
        context += c["text"] + "\n\n"
        #else:
        #    break

    return context

def rewrite_query(question):
    prompt = f"""
Rewrite the following question to make it more specific and detailed for document search.

Do NOT answer the question.
Only rewrite it.
DO NOT add text like "here is your answer"

Question:
{question}

Rewritten question:
"""

    rewritten = query_llm(prompt)
    return rewritten.strip()

def generate_answer(question, context_chunks, conversation_summary):
    if not context_chunks:
        return "No relevant information found."

    context = build_context(context_chunks)

    prompt =  f"""
You are an internal company assistant.

Use the conversation summary, the context and your world knowledge to answer.

Conversation summary:
{conversation_summary}

Context:
{context}

Question:
{question}

Rules:
- Be concise unless specification required
- Use context and conversation summary when relevant
- If not enough info, say so
- Avoid talking about context or conversation history if not relevant
- When you answer based on the context and not from the summary or your knowledge,
 include the sources in the following way:

(Sources: source1.pdf,source2.txt, and so)

Answer:
"""

    answer = query_llm(prompt)


    return f"{answer}"

def get_rag_answer(question, conversation_summary=""):
    
    stored_chunks,embeddings = INDEX if INDEX else load_index()

    if embeddings is None or stored_chunks is None:
        return "No documents available. Please upload documents first."
    
    
    """ action = decide_action(question)
    if action == "clarify":
        return "Could you clarify your question?"
    
    if action == "summarize":
        context_chunks = retrieve_context(question, stored_chunks)

        context = build_context(context_chunks)

        prompt = f
    Summarize the following company information:

    {context}

    Summary:
    

        answer = query_llm(prompt)

        return answer """
    
    context_chunks = retrieve_context(question, stored_chunks)
    
    answer = generate_answer(question, context_chunks, conversation_summary)
    

    return answer
