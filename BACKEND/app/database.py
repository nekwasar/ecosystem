from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from core.config import settings

# Database configuration - using SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import essential models to ensure tables are created
# This must be after Base is defined to avoid circular imports
from models.blog import BlogPost, BlogComment, BlogLike, TemporalUser, BlogView
from models.author import BlogAuthor

# Create tables
def create_tables():
    # Create tables with checkfirst=True to avoid errors if tables already exist
    try:
        print("🚀 Creating database tables...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Database tables created/verified successfully!")
        
        # List all tables that should exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Existing tables: {tables}")
        
        if 'blog_likes' in tables:
            print("✅ blog_likes table exists!")
        else:
            print("❌ blog_likes table is missing!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        raise

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()