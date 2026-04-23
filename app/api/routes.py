from sqlite3.dbapi2 import Timestamp

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.services.dependencies import get_current_user
from app.models.schemas import AnswerResponse, QuestionRequest
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.auth_models import RegisterRequest, LoginRequest
from app.rag.rag_pipeline import get_rag_answer
from app.services.llm_service import query_llm
from datetime import datetime, timezone
from sqlalchemy import func

router = APIRouter()


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == request.email).first()

    if existing:
        return {"error": "User already exists"}

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="user"
    )

    db.add(user)
    db.commit()

    return {"message": "User created"}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        return {"error": "Invalid credentials"}

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token}

@router.get("/conversations")
def get_conversations(user=Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.last_message_at.desc())
        .all()
    )

    return [
        {"id": c.id, "title": c.title}
        for c in conversations
    ]

@router.get("/conversations/{conv_id}")
def get_messages(conv_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        Message.conversation_id == conv_id
    ).all()

    for m in messages:
        m.timestamp = m.timestamp.replace(tzinfo=timezone.utc)
    
    return [
        {"role": m.role,
        "content": m.content,
        "timestamp": m.timestamp.isoformat()}
        for m in messages
    ]

@router.post("/ask")
def ask_question(
    request: QuestionRequest,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    askTime = datetime.now(timezone.utc)
    conversation : Conversation
    if request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == user.id
        ).first()
    else:
        prompt =f"""Give me a short title as plain text (without decorators) for a conversation
        that started with the following message:
        {request.question}
        """
        conversation = Conversation(
            user_id=user.id,
            title=query_llm(prompt)
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 🔹 2. obtener historial
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).all()

    # 🔹 3. construir contexto
    history = "\n".join([
        f"{m.role}: {m.content}" for m in messages
    ])
    
    # 🔹 4. generar respuesta (tu RAG actual)
    answer = get_rag_answer(request.question, history)
    # 🔹 5. guardar mensajes
    responseTime = datetime.now(timezone.utc)
    db.add(Message(
        role="user",
        content=request.question,
        timestamp=askTime,
        conversation_id=conversation.id
    ))
    db.add(Message(
        role="ai",
        content=answer,
        timestamp = responseTime,
        conversation_id=conversation.id
    ))

    conversation.last_message_at = responseTime

    db.commit()
    
    return AnswerResponse(answer=answer,
                          conversation_id=conversation.id,
                          conversation=conversation.title,
                          timestamp=responseTime.isoformat())