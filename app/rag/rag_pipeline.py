from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_documents():
    with open("data/company_docs.txt", "r", encoding="utf-8") as f:
        return f.read()

def split_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

def build_index(chunks):
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index, embeddings

def retrieve_context(question, chunks, index, k=2):
    query_vector = model.encode([question])
    query_vector = np.array(query_vector)

    distances, indices = index.search(query_vector, k)

    return [chunks[i] for i in indices[0]]

def generate_answer(question, context_chunks):
    context = "\n".join(context_chunks)

    return f"""
Answer based on company documents:

{context}

Question: {question}
"""

def get_rag_answer(question: str) -> str:
    text = load_documents()
    chunks = split_text(text)

    index, _ = build_index(chunks)

    relevant_chunks = retrieve_context(question, chunks, index)

    return generate_answer(question, relevant_chunks)