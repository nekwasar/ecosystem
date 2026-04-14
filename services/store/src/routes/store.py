from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.product import Product, Order, Category
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    price: float
    category: Optional[str]
    images: List[str]
    stock: int

    class Config:
        from_attributes = True


@router.get("/api/products", response_model=List[ProductResponse])
async def get_products(category: Optional[str] = None, limit: int = 20, db: Session = Depends(get_db)):
    query = db.query(Product).filter(Product.is_active == True)
    if category:
        query = query.filter(Product.category == category)
    return query.limit(limit).all()


@router.get("/api/products/{slug}", response_model=ProductResponse)
async def get_product(slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [{"id": c.id, "name": c.name, "slug": c.slug} for c in categories]


@router.post("/api/orders")
async def create_order(order_data: dict, db: Session = Depends(get_db)):
    order = Order(**order_data)
    db.add(order)
    db.commit()
    return {"success": True, "order_id": order.id}


@router.get("/api/orders/{order_number}")
async def get_order(order_number: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
