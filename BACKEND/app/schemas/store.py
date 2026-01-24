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
    
    # Metadata
    version: Optional[str] = None
    tags: Optional[List[str]] = None
    preview_url: Optional[str] = None

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

# --- Order Schemas ---

class OrderItemBase(BaseModel):
    product_name: str
    sku: Optional[str] = None
    unit_price: float
    quantity: int

class OrderItem(OrderItemBase):
    id: int
    product_id: int
    
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    status: str

class OrderUpdate(OrderBase):
    payment_status: Optional[str] = None

class Order(OrderBase):
    id: int
    order_number: str
    user_id: Optional[int]
    guest_email: Optional[str]
    total_amount: float
    currency: str
    payment_status: Optional[str]
    created_at: datetime
    items: List[OrderItem] = []
    
    class Config:
        orm_mode = True

# --- Discount Schemas ---

class DiscountBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str = "percentage"
    value: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_uses: Optional[int] = None
    is_active: bool = True

class DiscountCreate(DiscountBase):
    pass

class DiscountUpdate(BaseModel):
    description: Optional[str] = None
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None
    max_uses: Optional[int] = None

class Discount(DiscountBase):
    id: int
    used_count: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# --- Shipping Schemas ---

class ShippingRateBase(BaseModel):
    name: str # Standard
    price: float
    min_order_price: Optional[float] = None
    max_order_price: Optional[float] = None

class ShippingRateCreate(ShippingRateBase):
    pass

class ShippingRate(ShippingRateBase):
    id: int
    zone_id: int
    
    class Config:
        orm_mode = True

class ShippingZoneBase(BaseModel):
    name: str
    countries: List[str] # ["US", "CA"]

class ShippingZoneCreate(ShippingZoneBase):
    rates: List[ShippingRateCreate] = []

class ShippingZone(ShippingZoneBase):
    id: int
    rates: List[ShippingRate] = []
    
    class Config:
        orm_mode = True
