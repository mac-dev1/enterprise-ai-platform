from app.rag.rag_pipeline import get_rag_answer

def get_answer(question: str) -> str:
    return get_rag_answer(question)