from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.store import (
    Product, ProductCategory, ProductMedia, ProductAccessRequest, 
    ProductType, BillingScheme, AccessStatus
)
from schemas.store import (
    ProductCreate, ProductUpdate, Product as ProductSchema,
    CategoryCreate, Category as CategorySchema,
    AccessRequestUpdate, AccessRequest as AccessRequestSchema
)
import stripe
from core.config import settings

router = APIRouter()

# --- PRODUCT MANAGEMENT ---

@router.post("/products", response_model=ProductSchema)
async def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a highly customizable product:
    - Supports Subscription intervals logic
    - Stripe Product/Price auto-creation logic would go here
    """
    # 1. Check Slug
    if db.query(Product).filter(Product.slug == product.slug).first():
        raise HTTPException(400, "Slug already exists")

    # 2. Create DB Product
    db_product = Product(**product.dict())
    db.add(db_product)
    
    # 3. (Optional) Sync with Stripe immediately if keys are set
    if settings.stripe_secret_key and product.billing_scheme == BillingScheme.RECURRING:
        try:
            stripe.api_key = settings.stripe_secret_key
            # simplify for demo: create Product -> create Price
            stripe_prod = stripe.Product.create(name=product.name)
            stripe_price = stripe.Price.create(
                product=stripe_prod.id,
                unit_amount=int(product.price * 100),
                currency=product.currency.lower(),
                recurring={"interval": product.subscription_interval} if product.subscription_interval else None
            )
            db_product.stripe_product_id = stripe_prod.id
            db_product.stripe_price_id = stripe_price.id
        except Exception as e:
            # Decide if we soft-fail or hard-fail. For Enterprise, maybe log warning but continue?
            pass

    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/products/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """Update detailed product attributes"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")
        
    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
        
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Soft delete or Hard delete logic"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

# --- MEDIA GALLERY MANAGEMENT ---

@router.post("/products/{product_id}/media")
async def add_product_media(
    product_id: int,
    file_url: str = Body(..., embed=True),
    media_type: str = Body("image", embed=True),
    is_hero: bool = Body(False, embed=True),
    db: Session = Depends(get_db)
):
    """
    Add Image OR Video to product gallery.
    If is_hero is True, it unsets other heroes first.
    """
    if is_hero:
        # Unset previous hero
        db.query(ProductMedia).filter(
            ProductMedia.product_id == product_id, 
            ProductMedia.is_hero == True
        ).update({"is_hero": False})
    
    media = ProductMedia(
        product_id=product_id,
        file_url=file_url,
        media_type=media_type, # 'image' or 'video'
        is_hero=is_hero
    )
    db.add(media)
    db.commit()
    return {"message": "Media added"}

# --- ACCESS REQUEST VETTING (The "Gate") ---

@router.get("/access-requests", response_model=List[AccessRequestSchema])
async def list_access_requests(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Admin Queue: See who wants to buy your $50k domain"""
    query = db.query(ProductAccessRequest)
    if status:
        query = query.filter(ProductAccessRequest.status == status)
    return query.order_by(ProductAccessRequest.created_at.desc()).all()

@router.put("/access-requests/{request_id}/review")
async def review_access_request(
    request_id: int,
    decision: AccessRequestUpdate,
    db: Session = Depends(get_db)
):
    """
    Approve or Reject a buyer.
    - If Approved: Emails the user "You're in. Go Buy."
    """
    req = db.query(ProductAccessRequest).filter(ProductAccessRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found")
        
    req.status = decision.status
    if decision.nda_signed:
        req.nda_signed_at = datetime.utcnow()
        
    db.commit()
    # TODO: Trigger Email Notification Service here
    return {"message": f"Request {decision.status}"}

# --- CATEGORY MANAGEMENT ---

@router.post("/categories", response_model=CategorySchema)
async def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db)
):
    db_cat = ProductCategory(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat
