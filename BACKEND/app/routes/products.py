from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.product import LegacyProduct as Product
from schemas import Product, ProductCreate

router = APIRouter()

@router.get("/", response_model=list[Product])
async def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all active products"""
    products = db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=Product)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product (admin only)"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """Update a product (admin only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product (admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@router.get("/type/{product_type}", response_model=list[Product])
async def get_products_by_type(product_type: str, db: Session = Depends(get_db)):
    """Get products by type (protip, app, ebook, premium)"""
    products = db.query(Product).filter(
        Product.product_type == product_type,
        Product.is_active == True
    ).all()
    return products