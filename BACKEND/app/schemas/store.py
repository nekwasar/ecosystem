from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Enums
from models.store import ProductType, BillingScheme, AccessStatus, OrderStatus

# --- Product Schemas ---

class ProductMediaBase(BaseModel):
    file_url: str
    media_type: str = "image"
    is_hero: bool = False
    sort_order: int = 0

class ProductMediaCreate(ProductMediaBase):
    pass

class ProductMedia(ProductMediaBase):
    id: int
    product_id: int

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    slug: str
    sku: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: float
    sale_price: Optional[float] = None
    currency: str = "USD"
    
    # Types & Billing
    product_type: str = ProductType.DIGITAL_DOWNLOAD
    billing_scheme: str = BillingScheme.ONE_TIME
    subscription_interval: Optional[str] = None
    
    # Privacy
    is_private_listing: bool = False
    
    # Inventory
    stock_quantity: int = -1
    is_active: bool = True
    
    # Config
    download_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    images: List[ProductMedia] = []

    class Config:
        orm_mode = True

# --- Access Request Schemas ---

class AccessRequestBase(BaseModel):
    linkedin_profile: str
    message: Optional[str] = None

class AccessRequestCreate(AccessRequestBase):
    pass

class AccessRequestUpdate(BaseModel):
    status: str
    nda_signed: bool = False

class AccessRequest(AccessRequestBase):
    id: int
    user_id: int
    product_id: int
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# --- Category Schemas ---

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    children: List['Category'] = []

    class Config:
        orm_mode = True
