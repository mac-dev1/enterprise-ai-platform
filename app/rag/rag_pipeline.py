from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
import re

INDEX_PATH = "data/index/faiss.index"
CHUNKS_PATH = "data/index/chunks.pkl"

# Load model once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_documents():
    with open("data/company_docs.txt", "r", encoding="utf-8") as f:
        return f.read()

def split_text(text):
     # Normalizar saltos de línea
    text = text.replace("\r\n", "\n")

    # Separar por bloques con títulos
    sections = re.split(r"\n(?=[A-Z][a-zA-Z ]+:\n)", text)

    return [section.strip() for section in sections if section.strip()]

def build_index(new_chunks, source_name):
    # Load existing data
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, "rb") as f:
            stored_chunks = pickle.load(f)
    else:
        stored_chunks = []

    # Add new chunks with metadata
    for chunk in new_chunks:
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

def retrieve_context(question, stored_chunks, index, k=1):
    query_vector = model.encode([question])
    query_vector = np.array(query_vector)

    distances, indices = index.search(query_vector, k)

    # Threshold para evitar resultados irrelevantes
    if distances[0][0] > 1.2:
        return []

    return [stored_chunks[i] for i in indices[0]]

def generate_answer(question, context_chunks):
    if not context_chunks:
        return "No relevant information found."

    chunk = context_chunks[0]

    return f"""
Answer:
{chunk['text']}

(Source: {chunk['source']})
"""

def get_rag_answer(question: str) -> str:
    index, stored_chunks = load_index()

    if index is None or stored_chunks is None:
        return "No documents available. Please upload documents first."

    relevant_chunks = retrieve_context(question, stored_chunks, index)
    print("CHUNKS:", stored_chunks)
    return generate_answer(question, relevant_chunks)