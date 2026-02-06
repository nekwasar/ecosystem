import os
import argparse
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Setup database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define minimal BlogPost model for insertion
class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    excerpt = Column(Text)
    content = Column(Text)
    author = Column(String(255), nullable=False, default='Moltbot')
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now)

def create_draft(title, content, slug, excerpt=""):
    session = SessionLocal()
    try:
        new_post = BlogPost(
            title=title,
            content=content,
            slug=slug,
            excerpt=excerpt,
            author="Moltbot",
            published_at=None,  # Explicitly None for draft
        )
        session.add(new_post)
        session.commit()
        print(f"Success: Draft '{title}' created with ID: {new_post.id}")
    except Exception as e:
        session.rollback()
        print(f"Error creating draft: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a blog post draft directly in the DB")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--content", required=True, help="Post content (Markdown supported)")
    parser.add_argument("--slug", required=True, help="URL-friendly slug")
    parser.add_argument("--excerpt", default="", help="Short summary")

    args = parser.parse_args()
    create_draft(args.title, args.content, args.slug, args.excerpt)
