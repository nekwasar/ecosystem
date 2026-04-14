from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    content = Column(Text)
    excerpt = Column(Text)
    author = Column(String(255), default="NekwasaR")
    
    template_type = Column(String(50), default="template1")
    featured_image = Column(String(500))
    video_url = Column(String(500))
    
    section = Column(String(100), default="others", index=True)
    tags = Column(JSON, default=list)
    
    priority = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BlogComment(Base):
    __tablename__ = "blog_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, nullable=False, index=True)
    author_name = Column(String(255), nullable=False)
    author_email = Column(String(255))
    content = Column(Text, nullable=False)
    
    is_approved = Column(Boolean, default=True)
    parent_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BlogTag(Base):
    __tablename__ = "blog_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    color = Column(String(20), default="#6366f1")
    post_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BlogAuthor(Base):
    __tablename__ = "blog_authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    bio = Column(Text)
    avatar_image = Column(String(500))
    cover_image = Column(String(500))
    expert_tags = Column(JSON, default=list)
    social_links = Column(JSON, default=list)
    books = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsletterSubscriber(Base):
    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
