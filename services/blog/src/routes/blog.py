from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.blog import BlogPost, BlogComment, BlogTag, NewsletterSubscriber
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    author: str
    published_at: Optional[str]
    featured_image: Optional[str]
    tags: List[str]
    view_count: int
    template_type: str
    is_featured: bool

    class Config:
        from_attributes = True


@router.get("/api/posts", response_model=List[PostResponse])
async def get_posts(section: Optional[str] = None, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(BlogPost).filter(BlogPost.published_at.isnot(None))
    if section:
        query = query.filter(BlogPost.section == section)
    posts = query.order_by(BlogPost.published_at.desc()).limit(limit).all()
    return posts


@router.get("/api/posts/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/api/posts/section/{section}")
async def get_posts_by_section(section: str, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(BlogPost).filter(
        BlogPost.section == section,
        BlogPost.published_at.isnot(None)
    ).order_by(BlogPost.published_at.desc()).limit(limit).all()
    return [{"id": p.id, "title": p.title, "slug": p.slug, "excerpt": p.excerpt} for p in posts]


@router.post("/api/comments")
async def create_comment(post_id: int, author_name: str, content: str, author_email: str = None, db: Session = Depends(get_db)):
    comment = BlogComment(post_id=post_id, author_name=author_name, content=content, author_email=author_email)
    db.add(comment)
    db.commit()
    return {"success": True}


@router.get("/api/comments/{post_id}")
async def get_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(BlogComment).filter(BlogComment.post_id == post_id, BlogComment.is_approved == True).all()
    return [{"id": c.id, "author_name": c.author_name, "content": c.content, "created_at": c.created_at} for c in comments]


@router.post("/api/newsletter/subscribe")
async def subscribe(email: str, name: str = None, db: Session = Depends(get_db)):
    existing = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == email).first()
    if existing:
        return {"message": "Already subscribed"}
    subscriber = NewsletterSubscriber(email=email, name=name)
    db.add(subscriber)
    db.commit()
    return {"success": True}


@router.get("/api/tags")
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(BlogTag).all()
    return [{"id": t.id, "name": t.name, "slug": t.slug, "color": t.color} for t in tags]
