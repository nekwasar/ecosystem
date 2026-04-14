from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging
import httpx

from ..database import get_db
from ..auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
)
from ..models.user import AdminUser

router = APIRouter()

logger = logging.getLogger(__name__)


# Custom 403 error handler
@router.get("/admin/403", response_class=HTMLResponse)
async def admin_403_error(request: Request):
    """Serve custom 403 error page"""
    return {"request": request}


@router.get("/admin/media", response_class=HTMLResponse)
async def admin_media_page(request: Request, db: Session = Depends(get_db)):
    return {"request": request}


# Dashboard API endpoints
@router.get("/api/admin/dashboard/kpi")
async def get_dashboard_kpi(current_user=Depends(get_current_active_user)):
    """Get dashboard KPI data"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.get_stats()


@router.get("/api/admin/security/users")
async def get_admin_users_api(
    current_user=Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get all admin users for management"""
    users = db.query(AdminUser).all()
    return {
        "users": users,
        "stats": {
            "totalUsers": len(users),
            "activeUsers": sum(1 for u in users if u.is_active),
            "superAdmins": sum(1 for u in users if u.is_superuser),
            "pendingUsers": 0,
            "usersChange": 0,
            "activeChange": 0,
            "superAdminChange": 0,
            "pendingChange": 0,
        },
    }


@router.get("/api/admin/security/apikeys")
async def get_admin_apikeys_api(current_user=Depends(get_current_active_user)):
    """Get all API keys for management"""
    return {
        "keys": [],
        "stats": {
            "totalApiKeys": 0,
            "activeKeys": 0,
            "expiredKeys": 0,
            "apiCallsToday": "0",
        },
    }


@router.get("/api/admin/dashboard/popular-content")
async def get_popular_content(current_user=Depends(get_current_active_user)):
    """Get popular content data"""
    return []


@router.get("/api/admin/dashboard/recent-activity")
async def get_recent_activity(current_user=Depends(get_current_active_user)):
    """Get recent activity data"""
    return []


@router.get("/api/admin/dashboard/chart-data")
async def get_dashboard_chart_data(
    period: str = "7d", current_user=Depends(get_current_active_user)
):
    """Get chart data for dashboard"""
    return {"labels": [], "views": [], "comments": []}


@router.get("/api/admin/dashboard/quick-stats")
async def get_quick_stats(current_user=Depends(get_current_active_user)):
    """Get quick stats data"""
    return {"searchQueries": 0, "avgResponseTime": 0, "uptime": 100, "dbSize": 0}


# Comments management
@router.get("/api/admin/blog/comments")
async def get_blog_comments(
    post_id: int = None,
    pending_only: bool = False,
    current_user=Depends(get_current_active_user),
):
    """Get blog comments for moderation"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.get_comments(post_id)


@router.put("/api/admin/blog/comments/{comment_id}/moderate")
async def moderate_blog_comment(
    comment_id: int, data: dict, current_user=Depends(get_current_active_user)
):
    """Approve or reject a comment"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.moderate_comment(
        comment_id, data.get("approved", True)
    )


# Blog management API endpoints
@router.get("/api/admin/blog/posts")
async def get_blog_posts(current_user=Depends(get_current_active_user)):
    """Get blog posts data for admin interface"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.get_posts()


@router.post("/api/admin/blog/posts")
async def create_blog_post(
    post_data: dict, current_user=Depends(get_current_active_user)
):
    """Create a new blog post"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.create_post(post_data)


@router.post("/api/admin/blog/drafts")
async def save_blog_draft(
    draft_data: dict, current_user=Depends(get_current_active_user)
):
    """Save a blog post as draft"""
    from ..clients.blog import BlogServiceClient

    draft_data["published_at"] = None
    return await BlogServiceClient.create_post(draft_data)


@router.put("/api/admin/blog/posts/{post_id}")
async def update_blog_post(
    post_id: int, post_data: dict, current_user=Depends(get_current_active_user)
):
    """Update a blog post"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.update_post(post_id, post_data)


@router.get("/api/admin/blog/posts/{post_id}")
async def get_blog_post(post_id: int, current_user=Depends(get_current_active_user)):
    """Get a single blog post"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.get_post(post_id)


@router.delete("/api/admin/blog/posts/{post_id}")
async def delete_blog_post(post_id: int, current_user=Depends(get_current_active_user)):
    """Delete a blog post"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.delete_post(post_id)


# Blog Tags API endpoints
@router.post("/api/admin/blog/tags")
async def create_blog_tag(
    tag_data: dict, current_user=Depends(get_current_active_user)
):
    """Create a new blog tag"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.create_tag(tag_data)


@router.get("/api/admin/blog/tags")
async def get_blog_tags(current_user=Depends(get_current_active_user)):
    """Get all blog tags"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.get_tags()


@router.delete("/api/admin/blog/tags/{tag_id}")
async def delete_blog_tag(tag_id: int, current_user=Depends(get_current_active_user)):
    """Delete a blog tag"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.delete_tag(tag_id)


# Blog Categories API endpoints
@router.get("/api/admin/blog/categories")
async def get_blog_categories(current_user=Depends(get_current_active_user)):
    """Get all blog categories"""
    from ..clients.blog import BlogServiceClient

    return await BlogServiceClient.get_categories()


# Admin authentication endpoints
@router.post("/admin/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        headers={
            "Set-Cookie": f"access_token={access_token}; HttpOnly; Secure; SameSite=Strict; Max-Age={ACCESS_TOKEN_EXPIRE_MINUTES * 60}; Path=/",
        },
    )


@router.post("/admin/logout")
async def admin_logout():
    """Handle admin logout"""
    return JSONResponse(
        content={"message": "Logged out successfully"},
        headers={
            "Set-Cookie": "access_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0; Path=/"
        },
    )


@router.get("/admin/check-auth")
async def check_auth(request: Request, current_user=Depends(get_current_active_user)):
    """Check if user is authenticated"""
    return JSONResponse(
        content={"authenticated": True, "username": current_user.username}
    )


@router.post("/admin/logout")
async def admin_logout():
    """Handle admin logout"""
    return JSONResponse(
        content={"message": "Logged out successfully"},
        headers={
            "Set-Cookie": "access_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0; Path=/"
        },
    )


# Generic Admin Page Route
@router.get("/admin/{section}/{page}", response_class=HTMLResponse)
async def admin_section_page(
    request: Request,
    section: str,
    page: str,
    current_user=Depends(get_current_active_user),
):
    """Serve admin section pages dynamically"""
    return {"request": request}


@router.get("/templates/{template_name}")
async def get_admin_template(
    template_name: str, current_user=Depends(get_current_active_user)
):
    """Serve admin page templates dynamically"""
    raise HTTPException(status_code=404, detail="Template not found")
