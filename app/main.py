from fastapi import FastAPI
from app.api.routes import router as auth_router
from fastapi.staticfiles import StaticFiles
from app.rag.index_builder import build_index
import os

from app.db.base import Base
from app.db.session import engine

# 👇 importar modelos (MUY IMPORTANTE)
from app.db.models.user import User
from app.db.models.conversation import Conversation
from app.db.models.message import Message

Base.metadata.create_all(bind=engine)

if not os.path.exists("data/index/chunks.pkl"):
    build_index()

app = FastAPI()

app.include_router(auth_router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")