from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from core.limiter import limiter
from auth import (
    authenticate_user, create_access_token, create_refresh_token, 
    create_mfa_token, verify_totp_code, generate_totp_secret, 
    get_totp_uri, generate_qr_code, get_current_active_user, get_current_superuser
)
from models.user import AdminUser as DBAdminUser
from schemas import (
    AdminUserCreate, AdminUser as AdminUserSchema, Token, AdminLogin, 
    TOTPSetup, TOTPVerify
)
import logging
from fastapi import Request

# Set up dedicated auth route logging
auth_route_logger = logging.getLogger('auth_routes')
auth_route_logger.setLevel(logging.DEBUG)

router = APIRouter()

@router.post("/register", response_model=AdminUserSchema)
async def register_admin(user: AdminUserCreate, db: Session = Depends(get_db)):
    """Register a new admin user (only for initial setup)"""
    # Check if user already exists
    db_user = db.query(DBAdminUser).filter(
        (DBAdminUser.username == user.username) | (DBAdminUser.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Create new admin user
    from auth import get_password_hash
    hashed_password = get_password_hash(user.password)
    db_user = DBAdminUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_superuser=True  # First user is superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return AdminUserSchema(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        created_at=db_user.created_at,
        last_login=db_user.last_login
    )

@router.post("/login")
@limiter.limit("5/10minutes")
async def login_for_access_token(
    response: Response, 
    request: Request, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """Login and get access token via HttpOnly cookies (Rec 6 & 7)"""
    user = authenticate_user(db, form_data.username, form_data.password)

    if user == "LOCKED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked due to too many failed attempts. Please contact the administrator for a manual reset.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Phase 4: Handle MFA (TOTP)
    if user.totp_enabled:
        mfa_token = create_mfa_token(data={"sub": user.username})
        return {
            "mfa_required": True,
            "mfa_token": mfa_token,
            "message": "Two-factor authentication required"
        }

    # Standard Success: Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Store refresh token for revocation support
    user.refresh_token = refresh_token
    db.commit()

    # HttpOnly Cookies for security
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=15 * 60
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=7 * 24 * 3600
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "message": "Login successful."
    }

@router.post("/verify-mfa")
async def verify_mfa(
    response: Response,
    request: Request,
    verify_data: TOTPVerify,
    db: Session = Depends(get_db)
):
    """Verify MFA code and issue final tokens"""
    from jose import jwt
    from auth import SECRET_KEY, ALGORITHM
    
    # Check for authentication header or temporary cookie
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing MFA session token")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        scope = payload.get("scope")
        
        if scope != "mfa_pending":
            raise HTTPException(status_code=401, detail="Invalid session scope")
            
        user = db.query(DBAdminUser).filter(DBAdminUser.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        # Verify TOTP Code
        if not verify_totp_code(user.totp_secret, verify_data.code):
            raise HTTPException(status_code=400, detail="Invalid 2FA code")
            
        # SUCCESS: Issue full tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        user.refresh_token = refresh_token
        db.commit()
        
        response.set_cookie(
            key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=15 * 60
        )
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=7 * 24 * 3600
        )
        
        return {"access_token": access_token, "message": "MFA verified. Login successful."}
        
    except Exception as e:
        auth_route_logger.error(f"❌ MFA Verification Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired MFA session")

@router.post("/mfa/setup", response_model=TOTPSetup)
async def setup_mfa(current_user: DBAdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Generate a new TOTP secret for the user to scan"""
    # If already enabled, they should probably use a 'reset' flow, but for now we re-generate
    secret = generate_totp_secret()
    current_user.totp_secret = secret
    db.commit()
    
    uri = get_totp_uri(secret, current_user.username)
    qr_code = generate_qr_code(uri)
    
    return {
        "secret": secret,
        "qr_code_uri": f"data:image/png;base64,{qr_code}"
    }

@router.post("/mfa/enable")
async def enable_mfa(verify_data: TOTPVerify, current_user: DBAdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Verify the first code and permanently enable MFA for the account"""
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="MFA setup not initiated")
        
    if verify_totp_code(current_user.totp_secret, verify_data.code):
        current_user.totp_enabled = True
        db.commit()
        return {"message": "MFA enabled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code. Please try again.")

@router.post("/mfa/disable")
async def disable_mfa(verify_data: TOTPVerify, current_user: DBAdminUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Disable MFA (requires a valid code for security)"""
    if verify_totp_code(current_user.totp_secret, verify_data.code):
        current_user.totp_enabled = False
        current_user.totp_secret = None
        db.commit()
        return {"message": "MFA disabled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")

@router.post("/logout")
async def logout(response: Response):
    """Clear security cookies"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """Exchange refresh token for a new access token (Rec 7)"""
    from jose import jwt
    from auth import SECRET_KEY, ALGORITHM
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh session not found")
        
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        scope = payload.get("scope")
        
        if not username or scope != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh scope")
            
        user = db.query(DBAdminUser).filter(DBAdminUser.username == username).first()
        if not user or user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Session revoked or invalid")
            
        # Issue new access token
        new_access = create_access_token(data={"sub": user.username})
        
        response.set_cookie(
            key="access_token", 
            value=new_access, 
            httponly=True, 
            secure=False, 
            samesite="lax",
            max_age=15 * 60
        )
        
        return {"access_token": new_access, "message": "Token refreshed"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

@router.get("/me", response_model=AdminUserSchema)
async def read_users_me(current_user: DBAdminUser = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

@router.get("/users", response_model=list[AdminUserSchema])
async def get_admin_users(
    skip: int = 0,
    limit: int = 100,
    current_user: DBAdminUser = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Get all admin users (superuser only)"""
    users = db.query(DBAdminUser).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/activate")
async def activate_admin_user(
    user_id: int,
    current_user: DBAdminUser = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Activate/deactivate admin user (superuser only)"""
    user = db.query(DBAdminUser).filter(DBAdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}

@router.delete("/users/{user_id}")
async def delete_admin_user(
    user_id: int,
    current_user: DBAdminUser = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Delete admin user (superuser only)"""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.query(DBAdminUser).filter(DBAdminUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}