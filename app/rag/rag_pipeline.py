from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_documents():
    with open("data/company_docs.txt", "r", encoding="utf-8") as f:
        return f.read()

def split_text(text):
    return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

def build_index(chunks):
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index, embeddings

def retrieve_context(question, chunks, index, k=1):
    query_vector = model.encode([question])
    query_vector = np.array(query_vector)

    distances, indices = index.search(query_vector, k)

    return [chunks[i] for i in indices[0]]

def generate_answer(question, context_chunks):
    if not context_chunks:
        return "No relevant information found."

    context = context_chunks[0]

    return f"""\nAnswer:\n\n{context}"""

def get_rag_answer(question: str) -> str:
    text = load_documents()
    chunks = split_text(text)

    index, _ = build_index(chunks)

    relevant_chunks = retrieve_context(question, chunks, index)

    return generate_answer(question, relevant_chunks)