import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .database import engine, Base
from .routes import blog as blog_router
from .middleware.admin_auth import AdminAuthMiddleware

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Blog Service...")
    Base.metadata.create_all(bind=engine)
    logger.info("Blog Service started")
    yield
    logger.info("Shutting down Blog Service...")


app = FastAPI(
    title="Blog Service",
    description="Blog Service for Nekwasar Ecosystem",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AdminAuthMiddleware)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/blog", response_class=HTMLResponse)
@app.get("/blog/", response_class=HTMLResponse)
async def blog_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(blog_router.router)

from .routes import admin as admin_router

app.include_router(admin_router.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "blog"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
