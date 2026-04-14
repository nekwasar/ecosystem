from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float)
    category = Column(String(100), index=True)
    tags = Column(JSON, default=list)
    images = Column(JSON, default=list)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255))
    total = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    items = Column(JSON, default=list)
    shipping_address = Column(JSON)
    payment_status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
