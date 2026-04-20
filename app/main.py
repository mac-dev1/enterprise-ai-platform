from fastapi import FastAPI
from app.api.routes import router
from fastapi.staticfiles import StaticFiles
from app.rag.index_builder import build_index
import os

if not os.path.exists("data/index/chunks.pkl"):
    build_index()

app = FastAPI()

app.include_router(router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")