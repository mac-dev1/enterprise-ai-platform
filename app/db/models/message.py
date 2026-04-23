from datetime import datetime, timezone
import time

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    role = Column(String)  # "user" o "ai"
    content = Column(String)

    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    timestamp = Column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    
    conversation = relationship("Conversation", back_populates="messages")