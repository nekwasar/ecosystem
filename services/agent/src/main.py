import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Agent Service...")
    Base.metadata.create_all(bind=engine)
    logger.info("Agent Service started")
    yield
    logger.info("Shutting down Agent Service...")


app = FastAPI(title="Agent Service", description="AI Agent Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent"}


@app.post("/api/agent/chat")
async def chat(message: dict):
    return {"response": "Agent response placeholder"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(app, host="0.0.0.0", port=port)
