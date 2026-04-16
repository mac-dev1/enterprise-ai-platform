from fastapi import APIRouter
from app.models.schemas import QuestionRequest, AnswerResponse
from app.services.qa_service import get_answer

router = APIRouter()

@router.get("/")
def root():
    return {"message": "API is running"}

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    answer = get_answer(request.question)
    return AnswerResponse(answer=answer)