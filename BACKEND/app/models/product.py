from sqlalchemy import Column, Integer, String, Text, Boolean, DECIMAL
from database import Base

class LegacyProduct(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    product_type = Column(String(50))  # 'protip', 'app', 'ebook', 'premium'
    file_url = Column(String(500))
    stock_quantity = Column(Integer)
    is_active = Column(Boolean, default=True)