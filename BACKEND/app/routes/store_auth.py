from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from core.config import settings
from typing import Optional
from models.user import User
from services.email_service import email_service
from jose import jwt
from datetime import datetime, timedelta
import requests

# OAuth Lib (Could use Authlib, but basic requests works for now)
import json

router = APIRouter()

# --- GOOGLE OAUTH CONFIG ---
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = f"{settings.DOMAIN}/api/auth/callback/google"

@router.get("/login/google")
async def login_google():
    """Redirect user to Google Consent Screen"""
    scope = "openid email profile"
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope={scope}&access_type=offline"
    }

@router.get("/callback/google")
async def callback_google(code: str, response: Response, db: Session = Depends(get_db)):
    """Handle the callback from Google, create/get User, and set Session Cookie"""
    
    # 1. Exchange Code for Token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    try:
        res = requests.post(token_url, data=data)
        token_data = res.json()
        access_token = token_data.get("access_token")
        
        # 2. Get User Info
        user_info = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"}).json()
        
        email = user_info.get("email")
        google_id = user_info.get("id")
        
        # 3. Find or Create User
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=user_info.get("name"),
                avatar_url=user_info.get("picture"),
                google_id=google_id
            )
            db.add(user)
        else:
            # Update data
            if not user.google_id: user.google_id = google_id
            if not user.avatar_url: user.avatar_url = user_info.get("picture")
            user.last_login = datetime.utcnow()
            
        db.commit()
        db.refresh(user)
        
        # 4. Create Session Token (JWT)
        # Using a simpler logic than Admin Auth for Store Users (Long lived session)
        session_token = create_store_token(user.id)
        
        # 5. Redirect to Store
        response = Response(status_code=302)
        response.headers["Location"] = "/store?login=success"
        response.set_cookie(key="store_session", value=session_token, httponly=True, max_age=86400 * 30) # 30 Days
        return response
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/magic-link")
async def send_magic_link(
    email: dict, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send a login link to any email"""
    user_email = email.get("email")
    if not user_email:
        raise HTTPException(400, "Email required")
        
    # Check/Create User
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email)
        db.add(user)
        db.commit()
    
    # Generate Token
    token = create_store_token(user.id, expires_delta=timedelta(minutes=15))
    link = f"{settings.DOMAIN}/api/auth/magic-login?token={token}"
    
    # Send Email
    await email_service.send_email_background(
        background_tasks,
        user_email,
        "Your Login Link",
        f"<a href='{link}'>Click here to log in</a> to NekwasaR Store."
    )
    
    return {"message": "Link sent"}

@router.get("/magic-login")
async def magic_login(token: str):
    """Verify magic link token and set session cookie"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        response = Response(status_code=302)
        response.headers["Location"] = "/store?login=success"
        
        # Re-issue long-lived token
        new_token = create_store_token(user_id)
        response.set_cookie(key="store_session", value=new_token, httponly=True, max_age=86400 * 30)
        
        return response
    except:
        return {"error": "Invalid or expired link"}

@router.get("/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get currently logged in user from Cookie"""
    token = request.cookies.get("store_session")
    if not token:
        raise HTTPException(401, "Not logged in")
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar": user.avatar_url,
            "is_verified": user.is_verified_buyer
        }
    except:
        raise HTTPException(401, "Invalid session")

# -- Helper --
def create_store_token(user_id: int, expires_delta: timedelta = None):
    to_encode = {"sub": str(user_id)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
