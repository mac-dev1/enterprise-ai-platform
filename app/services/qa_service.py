from app.rag.rag_pipeline import get_rag_answer

def get_answer(question: str) -> dict:
    return get_rag_answer(question)