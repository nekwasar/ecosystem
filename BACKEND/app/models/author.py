from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, func
from database import Base

class BlogAuthor(Base):
    __tablename__ = "blog_authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False, index=True)
    bio = Column(Text)  # Rich text bio
    avatar_image = Column(String(500)) # URL to avatar
    cover_image = Column(String(500)) # URL to profile cover/banner
    
    # Social Media
    social_links = Column(JSON)  # {"twitter": "url", "linkedin": "url", ...}
    
    # Meta
    expert_tags = Column(JSON) # ["Tech", "AI", "Design"] - specialization tags
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

