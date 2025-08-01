from fastapi import FastAPI
from app.api import health_router, chat_router, auth_router
from app.api.url import router as url_router

app = FastAPI()

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(url_router) 