from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base

from datetime import datetime

class User(Base):
    """
    Standard User for the Platform / Store.
    Supports OAuth (Google) and Magic Link (Passwordless).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Auth Providers
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    linkedin_id = Column(String(255), unique=True, index=True, nullable=True)
    
    # Store Profile
    business_email = Column(String(255), nullable=True) # For vetting
    is_verified_buyer = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Brute-force protection fields
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    
    # Session Persistence
    refresh_token = Column(String(255), nullable=True)
    
    # 2FA / TOTP (Phase 4)
    totp_secret = Column(String(32), nullable=True)
    totp_enabled = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))