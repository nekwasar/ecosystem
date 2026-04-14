from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models.blog import BlogPost, BlogComment, BlogTag, NewsletterSubscriber

router = APIRouter()


class PostCreate(BaseModel):
    title: str
    slug: str
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    section: Optional[str] = "others"
    tags: Optional[List[str]] = []
    is_featured: Optional[bool] = False
    published_at: Optional[str] = None


class PostUpdate(PostCreate):
    pass


# Posts management
@router.get("/api/admin/posts")
async def get_posts_admin(
    status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)
):
    query = db.query(BlogPost)

    if status == "published":
        query = query.filter(BlogPost.published_at.isnot(None))
    elif status == "draft":
        query = query.filter(BlogPost.published_at.is_(None))

    posts = query.order_by(BlogPost.created_at.desc()).limit(limit).all()
    total = query.count()
    published = db.query(BlogPost).filter(BlogPost.published_at.isnot(None)).count()
    drafts = db.query(BlogPost).filter(BlogPost.published_at.is_(None)).count()

    return {
        "posts": posts,
        "stats": {
            "totalPosts": total,
            "publishedCount": published,
            "draftCount": drafts,
            "scheduledCount": 0,
        },
    }


@router.get("/api/admin/posts/{post_id}")
async def get_post_admin(post_id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/api/admin/posts")
async def create_post_admin(post_data: PostCreate, db: Session = Depends(get_db)):
    post = BlogPost(**post_data.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"success": True, "post_id": post.id, "post": post}


@router.put("/api/admin/posts/{post_id}")
async def update_post_admin(
    post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    for key, value in post_data.dict(exclude_unset=True).items():
        setattr(post, key, value)

    db.commit()
    return {"success": True, "post_id": post_id}


@router.delete("/api/admin/posts/{post_id}")
async def delete_post_admin(post_id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"success": True}


# Tags management
@router.get("/api/admin/tags")
async def get_tags_admin(db: Session = Depends(get_db)):
    tags = db.query(BlogTag).all()
    return {"tags": tags}


@router.post("/api/admin/tags")
async def create_tag_admin(tag_data: dict, db: Session = Depends(get_db)):
    tag = BlogTag(**tag_data)
    db.add(tag)
    db.commit()
    return {"success": True}


@router.delete("/api/admin/tags/{tag_id}")
async def delete_tag_admin(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(BlogTag).filter(BlogTag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return {"success": True}


# Categories placeholder
@router.get("/api/admin/categories")
async def get_categories_admin():
    return {"categories": []}


# Comments management
@router.get("/api/admin/comments")
async def get_comments_admin(
    post_id: Optional[int] = None,
    pending_only: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(BlogComment)
    if post_id:
        query = query.filter(BlogComment.post_id == post_id)
    if pending_only:
        query = query.filter(BlogComment.is_approved == False)

    comments = query.order_by(BlogComment.created_at.desc()).all()
    return {"comments": comments}


@router.put("/api/admin/comments/{comment_id}/moderate")
async def moderate_comment_admin(
    comment_id: int, data: dict, db: Session = Depends(get_db)
):
    comment = db.query(BlogComment).filter(BlogComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.is_approved = data.get("approved", True)
    db.commit()
    return {"success": True}


# Stats endpoint for dashboard
@router.get("/api/admin/stats")
async def get_blog_stats(db: Session = Depends(get_db)):
    total_posts = db.query(func.count(BlogPost.id)).scalar() or 0
    total_comments = db.query(func.count(BlogComment.id)).scalar() or 0
    total_subscribers = db.query(func.count(NewsletterSubscriber.id)).scalar() or 0
    total_views = db.query(func.sum(BlogPost.view_count)).scalar() or 0

    return {
        "totalPosts": total_posts,
        "totalComments": total_comments,
        "totalSubscribers": total_subscribers,
        "totalViews": total_views,
        "postsChange": 0,
        "commentsChange": 0,
        "subscribersChange": 0,
        "viewsChange": 0,
    }
