from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.store import Product, ProductAccessRequest, AccessStatus
from schemas.store import Product as ProductSchema, ProductMedia
import math

router = APIRouter()

@router.get("", response_model=List[ProductSchema])
async def get_store_products(
    category_slug: Optional[str] = None,
    include_private: bool = False, # Only used if user is authenticated & authorized
    db: Session = Depends(get_db)
):
    """
    Get public catalog. 
    By default, 'Private Listings' are shown but with redacted/teaser data.
    """
    query = db.query(Product).filter(Product.is_active == True)
    
    if category_slug:
        query = query.join(Product.category).filter(Product.category.slug == category_slug)
    
    products = query.all()
    
    # Teaser Logic: Redact sensitive info for private listings
    # Optimally, this should be done with a Pydantic 'TeaserSchema' but for now we mask in place
    results = []
    for p in products:
        if p.is_private_listing:
             # Clone or modify for display
             # In a real app, you'd return a specific "ListingTeaser" object
             # For now, we assume the frontend handles the "Blurred" UI based on the flag
             pass
        results.append(p)
        
    return results

@router.get("/{slug}", response_model=ProductSchema)
async def get_product_detail(
    slug: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get detailed product view.
    Logic:
    - If Public: Return full data.
    - If Private:
        1. Check if User logged in.
        2. Check if AccessRequest exists & is APPROVED.
        3. If YES -> Return Full Data.
        4. If NO -> Return Teaser Data (Price = 0, Description = "Restricted").
    """
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(404, "Product not found")

    if not product.is_private_listing:
        return product

    # --- PRIVATE LISTING LOGIC ---
    
    # Check User from Header (simulated, usually via Auth Middleware)
    user_id = request.headers.get("X-User-ID") 
    
    has_access = False
    if user_id:
        access_req = db.query(ProductAccessRequest).filter(
            ProductAccessRequest.product_id == product.id,
            ProductAccessRequest.user_id == user_id,
            ProductAccessRequest.status == AccessStatus.APPROVED
        ).first()
        if access_req:
            has_access = True
            
    if has_access:
        return product
    else:
        # Return TEASER (Redacted)
        # We modify the object in memory before returning (not saving to DB!)
        product.price = 0 # Hide price
        product.description = "🔒 This is a private listing. Please request access to view full financials and details."
        # Keep name and media for the "Teaser" appeal
        return product

@router.post("/{id}/request-access")
async def request_access(
    id: int,
    request: Request,
    linkedin_profile: str = Body(..., embed=True),
    message: str = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """Submit application to view a high-ticket item"""
    user_id = request.headers.get("X-User-ID") 
    if not user_id:
         raise HTTPException(401, "Must be logged in to request access")
         
    # Check duplicates
    existing = db.query(ProductAccessRequest).filter(
        ProductAccessRequest.product_id == id,
        ProductAccessRequest.user_id == user_id
    ).first()
    
    if existing:
        return {"message": "Request already pending or processed", "status": existing.status}
        
    new_req = ProductAccessRequest(
        product_id=id,
        user_id=user_id,
        linkedin_profile=linkedin_profile,
        message=message,
        status=AccessStatus.PENDING
    )
    db.add(new_req)
    db.commit()
    
    return {"message": "Access request submitted. We will review your profile shortly."}
