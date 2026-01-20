# Import all route modules to make them available
from . import contacts
from . import blogs
from . import products
from . import auth
from . import admin
from . import search
from . import newsletter
from . import analytics
from . import content

# Export the routers
from .contacts import router as contacts_router
from .blogs import router as blogs_router
from .products import router as products_router
from .auth import router as auth_router
from .admin import router as admin_router
from .store_admin import router as store_admin_router
from .store_front import router as store_front_router
from .store_checkout import router as store_checkout_router
from .store_auth import router as store_auth_router
from .search import router as search_router
from .newsletter import router as newsletter_router
from .analytics import router as analytics_router
from .content import router as content_router

# Create a unified router list for easy importing
all_routers = [
    contacts_router,
    blogs_router,
    products_router,
    auth_router,
    admin_router,
    search_router,
    newsletter_router,
    analytics_router,
    content_router,
]
