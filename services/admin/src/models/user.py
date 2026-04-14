from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from ..database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    role = Column(String(50), default="admin")
    
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(500), unique=True, nullable=False)
    device_fingerprint = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminRole(Base):
    __tablename__ = "admin_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSON)
    description = Column(Text)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
