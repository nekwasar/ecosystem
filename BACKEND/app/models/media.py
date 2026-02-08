from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from database import Base

class RouteType(str, enum.Enum):
    CDN = "CDN"
    SHARE = "SHARE"

class FileAsset(Base):
    __tablename__ = "file_assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)   # Name on disk (uuid.ext)
    original_name = Column(String(255), nullable=False) # Original upload name
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    
    # Routing Configuration
    route_type = Column(Enum(RouteType), default=RouteType.SHARE, nullable=False)
    custom_slug = Column(String(255), unique=True, index=True, nullable=False)
    
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Link to uploader (AdminUser or User)
    # For now, just store ID or string, or link to AdminUser if we had that imported.
    # Since AdminUser is in user.py, we can leave it loose for now or import it.
    uploaded_by_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Relationships
    # uploader = relationship("AdminUser") # constrained by circular imports potentially
