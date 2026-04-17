from app.services.llm_service import query_llm
import faiss
import numpy as np
import os
import pickle
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "data/index/faiss.index"
CHUNKS_PATH = "data/index/chunks.pkl"

# Load model once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_documents():
    with open("data/company_docs.txt", "r", encoding="utf-8") as f:
        return f.read()

def remove_table_of_contents(text):
    lines = text.split("\n")

    filtered = []
    for line in lines:
        # eliminar líneas tipo índice (muchos números)
        if len(line) < 100 and any(char.isdigit() for char in line):
            continue
        filtered.append(line)

    return "\n".join(filtered)

def split_text(text):
    text = text.replace("\r\n", "\n")

    text = remove_table_of_contents(text)

    lines = text.split("\n")

    chunks = []
    current_chunk = ""

    for line in lines:
        line = line.strip()

        # detectar títulos (heurística simple)
        if len(line) < 60 and line.istitle():
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                current_chunk = line
        else:
            current_chunk += " " + line

    if current_chunk:
        chunks.append(current_chunk.strip())

    # filtrar basura
    return [c for c in chunks if len(c) > 100]

def build_index(new_chunks, source_name):
    # Load existing data
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "rb") as f:
            stored_chunks = pickle.load(f)
    else:
        stored_chunks = []

    # Add new chunks with metadata
    existing_texts = set(c["text"] for c in stored_chunks)

    for chunk in new_chunks:
        if chunk not in existing_texts:
            stored_chunks.append({
                "text": chunk,
                "source": source_name
            })

    texts = [c["text"] for c in stored_chunks]

    embeddings = model.encode(texts)
    embeddings = np.array(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save everything
    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(stored_chunks, f)

    return index

def load_index():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        return None, None

    index = faiss.read_index(INDEX_PATH)

    with open(CHUNKS_PATH, "rb") as f:
        stored_chunks = pickle.load(f)

    return index, stored_chunks

def retrieve_context(question, stored_chunks, index, k=3):
    texts = [c["text"] for c in stored_chunks]

    # embeddings
    query_vec = model.encode([question])
    chunk_vecs = model.encode(texts)

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


def generate_answer(question, context_chunks):
    if not context_chunks:
        return "No relevant information found."

    context = "\n\n".join([c["text"] for c in context_chunks])

    prompt = f"""
You are an internal company assistant.

Answer the question based ONLY on the context below.

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    answer = query_llm(prompt)

    sources = ", ".join(set([c["source"] for c in context_chunks]))

    return f"""
{answer}

(Sources: {sources})
"""

def get_rag_answer(question: str) -> str:
    index, stored_chunks = load_index()

    if index is None or stored_chunks is None:
        return "No documents available. Please upload documents first."

    relevant_chunks = retrieve_context(question, stored_chunks, index)
    return generate_answer(question, relevant_chunks)