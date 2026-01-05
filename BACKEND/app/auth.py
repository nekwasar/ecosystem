from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyCookie
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models.user import AdminUser
from schemas import TokenData
from core.config import settings
import logging
import pyotp

# Set up dedicated auth logging
auth_logger = logging.getLogger('auth_flow')
auth_logger.setLevel(logging.DEBUG)

# Security configuration
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# Professional-grade password hashing with Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)
access_cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie_scheme = APIKeyCookie(name="refresh_token", auto_error=False)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt. Handles >72 chars by pre-hashing."""
    import hashlib
    # Pre-hash long passwords to bypass bcrypt's 72-byte limit (Rec 4)
    if len(password) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash safely."""
    import hashlib
    try:
        # Check if we need to pre-hash for verification
        if len(plain_password) > 72:
            plain_password = hashlib.sha256(plain_password.encode()).hexdigest()
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        auth_logger.error(f"❌ Password verification failed: {e}")
        return False

# --- TOTP / MFA Helpers (Phase 4) ---

def generate_totp_secret():
    """Generate a new random base32 TOTP secret"""
    return pyotp.random_base32()

def verify_totp_code(secret: str, code: str):
    """Verify a 6-digit TOTP code against the secret"""
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    # Allows for a small time drift (30 seconds)
    return totp.verify(code, valid_window=1)

def get_totp_uri(secret: str, username: str):
    """Generate a provisioning URI for QR codes"""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username, 
        issuer_name="NekwasaR Admin"
    )

def generate_qr_code(uri: str):
    """Generate a base64 encoded QR code PNG from a URI"""
    import qrcode
    import io
    import base64
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        auth_logger.error(f"❌ JWT CREATION FAILED - Error: {e}")
        raise

def create_refresh_token(data: dict):
    """Create a long-lived refresh token for session persistence"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "scope": "refresh"})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        auth_logger.error(f"❌ REFRESH TOKEN CREATION FAILED - Error: {e}")
        raise

def create_mfa_token(data: dict):
    """Create a short-lived token for MFA verification step"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire, "scope": "mfa_pending"})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        auth_logger.error(f"❌ MFA TOKEN CREATION FAILED - Error: {e}")
        raise

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password with lockout protection"""
    user = db.query(AdminUser).filter(AdminUser.username == username).first()

    if not user:
        return None, "INVALID"

    # Check if locked (Rec 5)
    if getattr(user, 'is_locked', False):
        auth_logger.warning(f"🔒 Account locked login attempt: {username}")
        return user, "LOCKED"

    if not verify_password(password, user.hashed_password):
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.is_locked = True
                auth_logger.error(f"❌ Account LOCKED after 5 failed attempts: {username}")
                db.commit()
                return user, "JUST_LOCKED"
            db.commit()
        return None, "INVALID"

    if not user.is_active:
        return None, "INACTIVE"

    # Success! Reset strikes
    if hasattr(user, 'failed_login_attempts'):
        user.failed_login_attempts = 0
        db.commit()
    return user, "SUCCESS"

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), 
    access_token: Optional[str] = Depends(access_cookie_scheme),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from Cookie (preferred) or Authorization Header"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Extraction: Cookie takes priority
    token = access_token
    if not token and credentials:
        token = credentials.credentials
        
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scope: str = payload.get("scope")

        if username is None or scope == "refresh":
            raise credentials_exception

        token_data = TokenData(username=username)

    except jwt.ExpiredSignatureError:
        auth_logger.warning("❌ TOKEN EXPIRED")
        raise credentials_exception
    except Exception as e:
        auth_logger.error(f"❌ JWT DECODE ERROR: {e}")
        raise credentials_exception

    try:
        user = db.query(AdminUser).filter(AdminUser.username == token_data.username).first()

        if user is None:
            raise credentials_exception
            
        if getattr(user, 'is_locked', False):
             auth_logger.warning(f"🔒 Blocked access to locked account: {user.username}")
             raise HTTPException(status_code=403, detail="Account is locked")

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise credentials_exception

def get_current_active_user(current_user: AdminUser = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_superuser(current_user: AdminUser = Depends(get_current_active_user)):
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Production Security Features (Commented for easy enabling)
"""
# HTTPS Enforcement (Uncomment in production)
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Rate Limiting (Uncomment in production)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Settings (Uncomment and configure for production)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers (Uncomment in production)
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])

# Input Validation Enhancement (Uncomment in production)
from pydantic import validator

class SecureContactCreate(BaseModel):
    name: str
    email: str
    message: str

    @validator('name')
    def name_must_be_valid(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name contains invalid characters')
        return v.strip()

    @validator('email')
    def email_must_be_valid(cls, v):
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower().strip()

    @validator('message')
    def message_must_be_valid(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        return v.strip()
"""