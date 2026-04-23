import os
import pickle
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.document_loader import load_documents

INDEX_PATH = "data/index"
CHUNKS_PATH = os.path.join(INDEX_PATH, "chunks.pkl")
EMB_PATH = os.path.join(INDEX_PATH, "embeddings.pkl")


def build_index():
    print("🔄 Building index...")

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = []
    for doc in docs:
        split = splitter.split_text(doc.page_content)
        for chunk in split:
            chunks.append({
                "text": chunk,
                "source": doc.metadata.get("source", "unknown")
            })

    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts)
    os.makedirs(INDEX_PATH, exist_ok=True)

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    with open(EMB_PATH, "wb") as f:
        pickle.dump(embeddings, f)

    print("✅ Index built")