import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

# Load env
load_dotenv(os.path.join(os.path.dirname(__file__), "app", ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("WARNING: DATABASE_URL not found, using sqlite fallback")
    DATABASE_URL = "sqlite:///./app/sql_app.db"

print(f"Connecting to: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("\n--- Blog Posts ---")
try:
    result = session.execute(text("SELECT id, title, slug, published_at FROM blog_posts"))
    posts = result.fetchall()
    if not posts:
        print("No posts found.")
    for p in posts:
        print(f"ID: {p.id} | Title: {p.title} | Slug: '{p.slug}' | Published: {p.published_at}")
except Exception as e:
    print(f"Error querying blog_posts: {e}")

session.close()
