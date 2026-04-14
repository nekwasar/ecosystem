import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ecosystem:password@localhost:5432/admin_db"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if os.getenv("TESTING") else None,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
