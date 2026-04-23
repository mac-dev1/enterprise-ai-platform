from pydantic import BaseModel
from datetime import datetime
from app.db.models import conversation

class QuestionRequest(BaseModel):
    question: str
    conversation_id: int | None = None

class AnswerResponse(BaseModel):
    answer: str
    conversation_id: int
    conversation: str
    timestamp: datetime