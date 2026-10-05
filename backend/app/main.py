from app.api.routes.chat import router as chat_router
from app.api.routes.providers import router as provider_router
from app.core.config import settings
from app.db import models
from app.db.database import Base, engine
from app.models import provider
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic Carbon-Aware AI Inference Orchestrator",
)
# Allow the local React/Vite frontend to call the API during development.
# Production origins can be supplied through FRONTEND_ORIGINS in .env.
allowed_origins = [
    origin.strip()
    for origin in settings.FRONTEND_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(provider_router)
app.include_router(chat_router)

@app.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "debug": settings.DEBUG,
    }
