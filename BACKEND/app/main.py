import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pathlib import Path
import uvicorn
import traceback
from sqlalchemy.orm import Session

from database import create_tables, SessionLocal, get_db
from routes import (
    contacts_router, blogs_router, products_router, auth_router, 
    admin_router, search_router, newsletter_router, analytics_router, content_router
)
from core.config import settings
from core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from scheduler import init_scheduler, start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NekwasaR Portfolio API",
    description="Backend API for NekwasaR's portfolio website",
    version="1.0.0"
)

# Add Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to every response (Rec 11)"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com https://cdn.jsdelivr.net; "
        "font-src 'self' https://fonts.gstatic.com https://unpkg.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https: https://cdn.tailwindcss.com; "
        "frame-ancestors 'none';"
    )
    return response

# Templates for admin pages
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Blog templates & statics
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BLOG_DIR = PROJECT_ROOT / "blog"
blog_templates = Jinja2Templates(directory=str(BLOG_DIR / "templates"))

# Add strftime filter to blog templates
from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import datetime

def strftime_filter(value, format):
    if not value:
        return ''
    # Handle both datetime objects and ISO format strings
    if isinstance(value, str):
        try:
            # Parse ISO format string to datetime object
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime(format)
        except (ValueError, AttributeError):
            return value
    elif isinstance(value, datetime):
        return value.strftime(format)
    else:
        return str(value)

blog_templates.env.filters['strftime'] = strftime_filter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contacts_router, prefix="/api/contacts", tags=["contacts"])
app.include_router(blogs_router, prefix="/api/blogs", tags=["blogs"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(newsletter_router, prefix="/api/newsletter", tags=["newsletter"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(admin_router, tags=["admin"])

# Mount static files for admin interface
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "portfolio")), name="static")

# Mount blog assets (css, js, img)
app.mount("/blog", StaticFiles(directory=str(BLOG_DIR)), name="blog-static")

# Add custom exception handler for 401/403 errors to show custom 403 page
from fastapi.responses import HTMLResponse
from fastapi.exception_handlers import http_exception_handler
from routes.admin import templates

async def custom_403_handler(request: Request, exc: HTTPException):
    """Custom handler for 401/403 errors to show custom 403 page"""
    if exc.status_code in [403, 401]:
        return templates.TemplateResponse("admin_403_error.html", {"request": request})
    # Fall back to default handler for other HTTP errors
    return await http_exception_handler(request, exc)

app.add_exception_handler(HTTPException, custom_403_handler)

# Global exception handler for validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors and log details"""
    logger.error(f"❌ VALIDATION ERROR: {exc.errors()}")
    logger.error(f"❌ VALIDATION ERROR BODY: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors(), "body": exc.body}
    )

app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Global exception handler for all other errors
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions and log details"""
    logger.error(f"❌ GENERAL ERROR: {type(exc).__name__}: {str(exc)}")
    logger.error(f"❌ ERROR TRACE: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": type(exc).__name__}
    )

app.add_exception_handler(Exception, general_exception_handler)

# Add traceback import
import traceback



@app.on_event("startup")
async def startup_event():
    """Create database tables and initialize scheduler on startup"""
    try:
        logger.info("🚀 Starting application initialization...")
        create_tables()
        logger.info("✅ Database tables created/verified")
        init_scheduler()
        logger.info("✅ Scheduler initialized")
        start_scheduler()
        logger.info("✅ Scheduler started")
        logger.info("✅ Application started successfully!")
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        logger.error(f"❌ Startup traceback: {traceback.format_exc()}")
        raise

# Default post data for SEO and sharing on non-article pages
DEFAULT_POST_DATA = {
    'title': 'NekwasaR Blog - Professional Insights & Innovation',
    'slug': '',
    'excerpt': 'Explore professional insights, analysis, and storytelling from NekwasaR.',
    'content': '',
    'author': 'NekwasaR',
    'published_at': None,
    'featured_image': None,
    'tags': [],
    'view_count': 0,
    'like_count': 0,
    'comment_count': 0
}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Domain-aware root route serving Portfolio, Blog, or Store based on Host header"""
    host = request.headers.get("host", "").lower()
    
    # 1. Portfolio Domain
    if host == "nekwasar.com":
        portfolio_path = PROJECT_ROOT / "portfolio" / "index.html"
        if portfolio_path.exists():
            return FileResponse(str(portfolio_path))
        
    # 2. Blog Domain
    if host == "blog.nekwasar.com":
        return blog_templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "current_year": datetime.utcnow().year,
                "post_data": DEFAULT_POST_DATA
            }
        )
        
    # 3. Store Domain
    if host == "store.nekwasar.com":
        store_path = PROJECT_ROOT / "store" / "index.html"
        if store_path.exists():
            return FileResponse(str(store_path))
            
    # 4. Admin/API Domain
    if host == "api.nekwasar.com":
        return RedirectResponse(url="/admin/login")
        
    # Fallback/Default: Portfolio
    portfolio_path = PROJECT_ROOT / "portfolio" / "index.html"
    if portfolio_path.exists():
        return FileResponse(str(portfolio_path))
    
    # Ultimate fallback if portfolio file is missing
    return HTMLResponse("OK")

# --- PORTFOLIO & STORE ASSET ROUTES (CSS, JS, IMG, FONTS) ---
# These routes serve static assets for the portfolio and store domains when they ask for relative paths (e.g. /css/main.css)
@app.get("/css/{rest:path}")
async def serve_css(request: Request, rest: str):
    host = request.headers.get("host", "").lower()
    folder = "portfolio" if host == "nekwasar.com" or host == "localhost:8000" else "store" if host == "store.nekwasar.com" else None
    if folder:
        path = PROJECT_ROOT / folder / "css" / rest
        if path.is_file(): return FileResponse(str(path))
    raise HTTPException(status_code=404)

@app.get("/js/{rest:path}")
async def serve_js(request: Request, rest: str):
    host = request.headers.get("host", "").lower()
    folder = "portfolio" if host == "nekwasar.com" or host == "localhost:8000" else "store" if host == "store.nekwasar.com" else None
    if folder:
        path = PROJECT_ROOT / folder / "js" / rest
        if path.is_file(): return FileResponse(str(path))
    raise HTTPException(status_code=404)

@app.get("/img/{rest:path}")
async def serve_img(request: Request, rest: str):
    host = request.headers.get("host", "").lower()
    folder = "portfolio" if host == "nekwasar.com" or host == "localhost:8000" else "store" if host == "store.nekwasar.com" else None
    if folder:
        path = PROJECT_ROOT / folder / "img" / rest
        if path.is_file(): return FileResponse(str(path))
    raise HTTPException(status_code=404)

@app.get("/fonts/{rest:path}")
async def serve_fonts(request: Request, rest: str):
    host = request.headers.get("host", "").lower()
    folder = "portfolio" if host == "nekwasar.com" or host == "localhost:8000" else "store" if host == "store.nekwasar.com" else None
    if folder:
        path = PROJECT_ROOT / folder / "fonts" / rest
        if path.is_file(): return FileResponse(str(path))
    raise HTTPException(status_code=404)

@app.get("/icon")
@app.get("/favicon.png")
@app.get("/favicon.ico")
async def serve_universal_favicon(request: Request):
    """Serve the central portfolio favicon as the one source of truth for all domains"""
    path = PROJECT_ROOT / "portfolio" / "favicon.png"
    if path.is_file(): 
        return FileResponse(str(path))
    raise HTTPException(status_code=404)

@app.get("/robots.txt")
async def serve_robots(request: Request):
    host = request.headers.get("host", "").lower()
    
    # Define robots content based on domain
    if host == "blog.nekwasar.com":
        content = "User-agent: *\nAllow: /\nSitemap: https://blog.nekwasar.com/sitemap.xml"
    elif host == "store.nekwasar.com":
        content = "User-agent: *\nAllow: /\nSitemap: https://store.nekwasar.com/sitemap.xml"
    else:
        content = "User-agent: *\nAllow: /\nSitemap: https://nekwasar.com/sitemap.xml"
        
    return Response(content=content, media_type="text/plain")

@app.get("/sitemap.xml")
async def serve_sitemap(request: Request, db: Session = Depends(get_db)):
    host = request.headers.get("host", "").lower()
    
    # 1. Handle Dynamic Blog Sitemap
    if host == "blog.nekwasar.com":
        from models.blog import BlogPost
        posts = db.query(BlogPost).filter(BlogPost.published_at.isnot(None)).all()
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        # Static Blog Pages
        for route in ['', 'latest', 'popular', 'featured', 'others', 'topics']:
            url = f"https://blog.nekwasar.com/{route}" if route else "https://blog.nekwasar.com/"
            xml_content += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
            
        # Dynamic Posts
        for post in posts:
            lastmod = post.updated_at.strftime('%Y-%m-%d') if post.updated_at else datetime.utcnow().strftime('%Y-%m-%d')
            xml_content += f'  <url>\n    <loc>https://blog.nekwasar.com/{post.slug}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.6</priority>\n  </url>\n'
            
        xml_content += '</urlset>'
        return Response(content=xml_content, media_type="application/xml")

    # 2. Handle Portfolio & Store Static Sitemaps
    folder = "portfolio" if host == "nekwasar.com" or host == "localhost:8000" else "store" if host == "store.nekwasar.com" else "portfolio"
    path = PROJECT_ROOT / folder / "sitemap.xml"
    if path.is_file(): 
        return FileResponse(str(path))
    
    raise HTTPException(status_code=404)

# SPA deep-link routes: serve the dynamic section pages
@app.get("/latest", response_class=HTMLResponse)
@app.get("/latest/", response_class=HTMLResponse)
async def blog_latest(request: Request):
    host = request.headers.get("host", "").lower()
    if host != "blog.nekwasar.com":
        return RedirectResponse(url=f"https://blog.nekwasar.com/latest")
    return blog_templates.TemplateResponse(
        "page_section.html",
        {"request": request, "section": "latest", "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

@app.get("/popular", response_class=HTMLResponse)
@app.get("/popular/", response_class=HTMLResponse)
async def blog_popular(request: Request):
    host = request.headers.get("host", "").lower()
    if host != "blog.nekwasar.com":
        return RedirectResponse(url=f"https://blog.nekwasar.com/popular")
    return blog_templates.TemplateResponse(
        "page_section.html",
        {"request": request, "section": "popular", "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

@app.get("/others", response_class=HTMLResponse)
@app.get("/others/", response_class=HTMLResponse)
async def blog_others(request: Request):
    host = request.headers.get("host", "").lower()
    if host != "blog.nekwasar.com":
        return RedirectResponse(url=f"https://blog.nekwasar.com/others")
    return blog_templates.TemplateResponse(
        "page_section.html",
        {"request": request, "section": "others", "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

@app.get("/featured", response_class=HTMLResponse)
@app.get("/featured/", response_class=HTMLResponse)
async def blog_featured(request: Request):
    host = request.headers.get("host", "").lower()
    if host != "blog.nekwasar.com":
        return RedirectResponse(url=f"https://blog.nekwasar.com/featured")
    return blog_templates.TemplateResponse(
        "page_section.html",
        {"request": request, "section": "featured", "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

@app.get("/topics", response_class=HTMLResponse)
@app.get("/topics/", response_class=HTMLResponse)
async def blog_topics(request: Request):
    host = request.headers.get("host", "").lower()
    if host != "blog.nekwasar.com":
        return RedirectResponse(url=f"https://blog.nekwasar.com/topics")
    return blog_templates.TemplateResponse(
        "page_section.html",
        {"request": request, "section": "topics", "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

# Dynamic blog post route
@app.get("/{slug}", response_class=HTMLResponse)
async def blog_post_by_slug(request: Request, slug: str, db: Session = Depends(get_db)):
    """Serve individual blog posts by slug with anti-leakage domain enforcement"""
    host = request.headers.get("host", "").lower()
    
    # 1. Assets Check: If on portfolio domain, check if it's a root-level file (like favicon.png)
    if host == "nekwasar.com" or host == "localhost:8000":
        portfolio_file = PROJECT_ROOT / "portfolio" / slug
        if portfolio_file.is_file():
            return FileResponse(str(portfolio_file))
            
    # 2. Anti-Leakage: Redirect to blog subdomain if NOT accessed through it
    if host != "blog.nekwasar.com" and host != "localhost:8000":
        return RedirectResponse(url=f"https://blog.nekwasar.com/{slug}")
        
    # 3. Serve individual blog posts by slug
    from models.blog import BlogPost

    # Skip if it's a known static route
    static_routes = ['latest', 'popular', 'featured', 'others', 'topics', 'template1', 'template2', 'template3']
    if slug in static_routes:
        raise HTTPException(status_code=404, detail="Page not found")

    # Look up post by slug
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Determine which template to use
    template_map = {
        'template1': 'template1-banner-image.html',
        'template2': 'template2-banner-video.html',
        'template3': 'template3-listing.html'
    }

    template_name = template_map.get(post.template_type, 'template1-banner-image.html')

    # Prepare post data for template
    post_data = {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'excerpt': post.excerpt,
        'content': post.content,
        'author': getattr(post, 'author', 'NekwasaR'),
        'published_at': post.published_at.isoformat() if post.published_at else None,
        'featured_image': post.featured_image,
        'tags': post.tags if post.tags else [],
        'view_count': post.view_count,
        'like_count': post.like_count,
        'comment_count': post.comment_count
    }

    return blog_templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "current_year": datetime.utcnow().year,
            "post_data": post_data
        }
    )

# Routes for specific blog templates
@app.get("/template1", response_class=HTMLResponse)
@app.get("/template1/", response_class=HTMLResponse)
async def blog_template1(request: Request):
    """Serve template1-banner-image.html"""
    return blog_templates.TemplateResponse(
        "template1-banner-image.html",
        {"request": request, "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

@app.get("/template2", response_class=HTMLResponse)
@app.get("/template2/", response_class=HTMLResponse)
async def blog_template2(request: Request):
    """Serve template2-banner-video.html"""
    return blog_templates.TemplateResponse(
        "template2-banner-video.html",
        {"request": request, "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

@app.get("/template3", response_class=HTMLResponse)
@app.get("/template3/", response_class=HTMLResponse)
async def blog_template3(request: Request):
    """Serve template3-listing.html"""
    return blog_templates.TemplateResponse(
        "template3-listing.html",
        {"request": request, "current_year": datetime.utcnow().year, "post_data": DEFAULT_POST_DATA}
    )

# Redirect misspelling /populer -> /popular
@app.get("/populer")
@app.get("/populer/")
async def populer_redirect():
    return RedirectResponse(url="/popular", status_code=301)

# Fallback admin dashboard routes (ensure rendering even if router load order conflicts)
@app.get("/admin/dashboard", response_class=HTMLResponse)
@app.get("/admin/dashboard/", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


# Production Security Features (Commented for easy enabling)
"""
# HTTPS Enforcement (Uncomment in production)
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)

# Rate Limiting (Uncomment in production)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Enhanced CORS (Uncomment and configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],  # Replace with your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security Headers (Uncomment in production)
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com", "www.yourdomain.com"])

# Input Validation Enhancement (Uncomment in production)
from pydantic import validator, BaseModel

class SecureContactCreate(BaseModel):
    name: str
    email: str
    message: str

    @validator('name')
    def name_must_be_valid(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not all(c.isalnum() or c.isspace() or c in ".-'" for c in v):
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

# Replace ContactCreate with SecureContactCreate in routes/contacts.py
"""

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="warning"
    )