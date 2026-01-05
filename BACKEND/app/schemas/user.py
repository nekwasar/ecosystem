from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdminUserBase(BaseModel):
    username: str
    email: str

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUser(AdminUserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    totp_enabled: bool = False

    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TOTPSetup(BaseModel):
    secret: str
    qr_code_uri: str

class TOTPVerify(BaseModel):
    code: str