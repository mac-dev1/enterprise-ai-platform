from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.models.schemas import QuestionRequest, AnswerResponse
from app.services.memory_service import update_summary_async
from app.services.session_service import get_session, update_session
from app.services.qa_service import get_answer
from app.services.pdf_loader import load_pdf
from app.rag.rag_pipeline import split_text
import asyncio

router = APIRouter()

sessions = {}

@router.post("/ask")
def ask_question(request: QuestionRequest, background_tasks: BackgroundTasks):
    question = request.question
    session_id = request.session_id

    if not question or not session_id:
        return {"error": "Missing question or session_id"}

    # 🔹 sesión
    session = get_session(session_id)
    summary = session["summary"]

    # 🔹 respuesta normal (NO streaming)
    answer = get_answer(question, summary)

    # 🔹 guardar conversación
    update_session(session_id, summary, question, answer)

    # 🔹 summary async
    background_tasks.add_task(
        update_summary_async,
        session_id,
        summary,
        question,
        answer
    )

    return AnswerResponse(answer=answer)

@router.get("/history/{session_id}")
def get_history(session_id: str):
    session = get_session(session_id)
    return session["history"]