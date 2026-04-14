import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .database import engine, Base
from .routes import admin as admin_router

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Admin Service...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Create default admin user if none exists
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    from .models.user import AdminUser
    from .auth import get_password_hash

    db = SessionLocal()
    try:
        if db.query(AdminUser).count() == 0:
            admin = AdminUser(
                username="admin",
                email="admin@nekwasar.com",
                hashed_password=get_password_hash("admin"),
                is_superuser=True,
            )
            db.add(admin)
            db.commit()
            logger.info("Created default admin user: admin / admin")
    finally:
        db.close()

    logger.info("Admin Service started successfully")
    yield

    logger.info("Shutting down Admin Service...")


# Create FastAPI application
app = FastAPI(
    title="Admin Service",
    description="Admin Dashboard for Nekwasar Ecosystem",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "views"))

# Static files
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Root route
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/", response_class=HTMLResponse)
async def admin_root(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_base.html", {"request": request})


# Include admin routes
app.include_router(admin_router.router)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
