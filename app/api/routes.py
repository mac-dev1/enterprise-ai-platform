from fastapi import APIRouter, UploadFile, File
from app.models.schemas import QuestionRequest, AnswerResponse
from app.services.qa_service import get_answer
from app.rag.rag_pipeline import split_text, build_index

router = APIRouter()

@router.get("/")
def root():
    return {"message": "API is running"}

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")

    chunks = split_text(content)
    build_index(chunks, file.filename)
    return {"message": "File processed and indexed successfully"}

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    answer = get_answer(request.question)
    return AnswerResponse(answer=answer)