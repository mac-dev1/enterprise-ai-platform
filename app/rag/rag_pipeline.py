from app.services.agent_service import decide_action
from app.services.llm_service import query_llm
from app.services.memory_service import update_summary
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
model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

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

def retrieve_context(question, stored_chunks, index, k=2):
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


def build_context(context_chunks, max_chars=1500):
    context = ""
    
    for c in context_chunks:
        if len(context) + len(c["text"]) < max_chars:
            context += c["text"] + "\n\n"
        else:
            break

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

Use the conversation summary and the context to answer.

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

Answer:
"""

    answer = query_llm(prompt)

    sources = ", ".join(set([c["source"] for c in context_chunks]))

    return f"""
{answer}

(Sources: {sources})
"""

def get_rag_answer(question, conversation_summary=""):
    index, stored_chunks = load_index()

    if index is None or stored_chunks is None:
        return "No documents available. Please upload documents first."
    
    action = decide_action(question)
    if action == "clarify":
        return ("Could you clarify your question?", conversation_summary)
    
    if action == "summarize":
        context_chunks = retrieve_context(question, stored_chunks, index)

        context = build_context(context_chunks)

        prompt = f"""
    Summarize the following company information:

    {context}

    Summary:
    """

        answer = query_llm(prompt)

        return (answer, conversation_summary)
    
    rewritten_question = rewrite_query(question)
    context_chunks = retrieve_context(rewritten_question, stored_chunks, index)
    
    answer = generate_answer(rewritten_question, context_chunks, conversation_summary)
    new_summary = update_summary(conversation_summary, question, answer)

    return (answer,new_summary)