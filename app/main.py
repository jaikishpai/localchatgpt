from fastapi import FastAPI
from app.api import health_router, chat_router

app = FastAPI()

app.include_router(health_router)
app.include_router(chat_router) 