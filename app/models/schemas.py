from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    response: dict