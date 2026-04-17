from fastapi import FastAPI
from app.api.routes import router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")