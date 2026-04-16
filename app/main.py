from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Enterprise AI Platform")

app.include_router(router)