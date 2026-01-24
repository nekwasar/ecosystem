from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL, ForeignKey, DateTime, JSON, Enum, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

# Enums for strict typing
class ProductType(str, enum.Enum):
    DIGITAL_DOWNLOAD = "digital_download"
    LICENSE_KEY = "license_key"
    PHYSICAL = "physical"
    TRANSFER_SERVICE = "transfer_service" # Domains, Apps
    SUBSCRIPTION = "subscription"

class BillingScheme(str, enum.Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"

class AccessStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TRANSFER_PENDING = "transfer_pending" # Manual handover

class ProductCategory(Base):
    __tablename__ = "store_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("store_categories.id"), nullable=True)
    
    # Relations
    children = relationship("ProductCategory", backref="parent", remote_side=[id])
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "store_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    sku = Column(String(100), unique=True, index=True)
    
    # Content
    description = Column(Text) # Rich text
    short_description = Column(Text) # For cards
    
    # Financials
    price = Column(DECIMAL(10, 2), nullable=False)
    sale_price = Column(DECIMAL(10, 2), nullable=True)
    currency = Column(String(3), default="USD")
    
    # Types & Billing
    product_type = Column(String(50), default=ProductType.DIGITAL_DOWNLOAD)
    billing_scheme = Column(String(50), default=BillingScheme.ONE_TIME)
    subscription_interval = Column(String(20), nullable=True) # "month", "year"
    stripe_price_id = Column(String(255)) # Stripe Price ID
    stripe_product_id = Column(String(255)) # Stripe Product ID
    
    # Metadata
    version = Column(String(50), nullable=True) # v1.0.0
    tags = Column(JSON, nullable=True) # ["react", "saas"]
    preview_url = Column(String(500), nullable=True) # Demo Link
    
    # Privacy / Vetting
    is_private_listing = Column(Boolean, default=False)
    
    # Inventory & Status
    stock_quantity = Column(Integer, default=-1) # -1 = infinite
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Delivery Config
    download_url = Column(String(500)) # For simple files
    license_generator_type = Column(String(50)) # "static_list" or "dynamic"
    
    # Relations
    category_id = Column(Integer, ForeignKey("store_categories.id"))
    category = relationship("ProductCategory", back_populates="products")
    images = relationship("ProductMedia", back_populates="product", cascade="all, delete-orphan")
    access_requests = relationship("ProductAccessRequest", back_populates="product")

class ProductMedia(Base):
    __tablename__ = "store_product_media"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("store_products.id"))
    file_url = Column(String(500), nullable=False)
    media_type = Column(String(20), default="image") # "image" or "video"
    is_hero = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    product = relationship("Product", back_populates="images")

class ProductAccessRequest(Base):
    __tablename__ = "store_access_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Assumes User model exists
    product_id = Column(Integer, ForeignKey("store_products.id"))
    
    # Vetting Data
    linkedin_profile = Column(String(500))
    message = Column(Text)
    status = Column(String(20), default=AccessStatus.PENDING)
    
    # Audit
    nda_signed_at = Column(DateTime, nullable=True)
    identity_verified = Column(Boolean, default=False) # Via Stripe Identity
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    product = relationship("Product", back_populates="access_requests")
    # user relationship would be defined if User model was imported

class Order(Base):
    __tablename__ = "store_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(100), unique=True, index=True) # e.g. ORD-2025-001
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for guest checkout
    guest_email = Column(String(255), nullable=True)
    
    # Financials
    total_amount = Column(DECIMAL(10, 2))
    tax_amount = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")
    
    # Status
    status = Column(String(50), default=OrderStatus.PENDING_PAYMENT)
    payment_status = Column(String(50)) # "paid", "unpaid", "failed"
    stripe_session_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    items = relationship("OrderItem", back_populates="order")
    messages = relationship("OrderMessage", back_populates="order")

class OrderItem(Base):
    __tablename__ = "store_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("store_orders.id"))
    product_id = Column(Integer, ForeignKey("store_products.id"))
    
    # Snapshot of data at time of purchase
    product_name = Column(String(255))
    sku = Column(String(100))
    unit_price = Column(DECIMAL(10, 2))
    quantity = Column(Integer, default=1)
    
    order = relationship("Order", back_populates="items")

class OrderMessage(Base):
    """Secure Chat for Transfer Services"""
    __tablename__ = "store_order_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("store_orders.id"))
    sender_type = Column(String(20)) # "user" or "admin"
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    order = relationship("Order", back_populates="messages")

class Subscription(Base):
    __tablename__ = "store_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("store_products.id"))
    
    stripe_subscription_id = Column(String(255), unique=True)
    status = Column(String(50)) # "active", "canceled", "past_due"
    current_period_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class DiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class Discount(Base):
    __tablename__ = "store_discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    
    discount_type = Column(String(20), default=DiscountType.PERCENTAGE)
    value = Column(DECIMAL(10, 2), nullable=False) # 10.00 for $10 or 10%
    
    # Limitations
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ShippingZone(Base):
    __tablename__ = "store_shipping_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # e.g. "North America", "Europe"
    countries = Column(JSON) # List of country codes ["US", "CA"]
    
    rates = relationship("ShippingRate", back_populates="zone", cascade="all, delete-orphan")

class ShippingRate(Base):
    __tablename__ = "store_shipping_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("store_shipping_zones.id"))
    
    name = Column(String(100)) # e.g. "Standard Shipping", "Express"
    price = Column(DECIMAL(10, 2), default=0.00)
    
    # Advanced logic placeholders
    min_order_price = Column(DECIMAL(10, 2), nullable=True)
    max_order_price = Column(DECIMAL(10, 2), nullable=True)
    
    zone = relationship("ShippingZone", back_populates="rates")
