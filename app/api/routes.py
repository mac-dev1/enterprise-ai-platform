from fastapi import APIRouter, UploadFile, File
from app.models.schemas import QuestionRequest, AnswerResponse
from app.services.session_service import get_summary, update_summary
from app.services.qa_service import get_answer
from app.services.pdf_loader import load_pdf
from app.rag.rag_pipeline import split_text, build_index

router = APIRouter()

sessions = {}

""" @router.post("/upload")
def upload_file(file: UploadFile = File(...)): 

    if file.filename.endswith(".pdf"):
        with open("temp.pdf", "wb") as f:
            f.write(file.file.read())

        content = load_pdf("temp.pdf")

    else:
        content = file.file.read().decode("utf-8")

    chunks = split_text(content)

    build_index(chunks, file.filename)

    return {"message": "File processed and indexed successfully"}
"""

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    session_id = request.session_id

    if session_id not in sessions:
        sessions[session_id] = ""

    summary = get_summary(session_id)

    ans,summ = get_answer(request.question,summary)

    update_summary(session_id,summ)

    return AnswerResponse(answer=ans)