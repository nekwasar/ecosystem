from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database import get_db
from models.store import (
    Product, ProductCategory, ProductMedia, ProductAccessRequest, 
    ProductType, BillingScheme, AccessStatus, Order
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

@router.get("/products", response_model=List[ProductSchema])
async def list_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List all products (Admin View - includes inactive)"""
    products = db.query(Product).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return products

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
    # 1. Custom Category Logic
    # The frontend sends '_category_name' (e.g. "SaaS" or "Custom") if not selecting by ID.
    # We need to resolve this to a real category_id before creating the product.
    product_data = product.dict()
    category_name = product_data.pop("_category_name", None) # Remove helper field
    
    if category_name:
        # Check if category exists
        slug = category_name.lower().replace(" ", "-")
        existing_cat = db.query(ProductCategory).filter(ProductCategory.slug == slug).first()
        
        if existing_cat:
            product_data["category_id"] = existing_cat.id
        else:
            # Create new category on the fly
            new_cat = ProductCategory(
                name=category_name, 
                slug=slug, 
                description=f"Auto-created category for {category_name}"
            )
            db.add(new_cat)
            db.commit()
            db.refresh(new_cat)
            product_data["category_id"] = new_cat.id

    # 2. Check Slug Uniqueness
    if db.query(Product).filter(Product.slug == product.slug).first():
        raise HTTPException(400, "Slug already exists")

    # 3. Create DB Product
    db_product = Product(**product_data)
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

@router.get("/categories", response_model=List[CategorySchema])
async def list_categories(db: Session = Depends(get_db)):
    categories = db.query(ProductCategory).all()
    return categories

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

@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(ProductCategory).filter(ProductCategory.id == category_id).first()
    if not db_cat:
        raise HTTPException(404, "Category not found")
    
    db.delete(db_cat)
    db.commit()
    return {"message": "Category deleted"}

# --- ORDER MANAGEMENT ---

from schemas.store import Order as OrderSchema, OrderUpdate

@router.get("/orders", response_model=List[OrderSchema])
async def list_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    orders = db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.put("/orders/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(404, "Order not found")
    
    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
        
    db.commit()
    db.refresh(db_order)
    return db_order


# --- CUSTOMER MANAGEMENT ---

from models.user import User
from schemas.user import User as UserSchema

@router.get("/customers", response_model=List[UserSchema])
async def list_customers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List all registered store customers"""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


# --- INVENTORY MANAGEMENT ---

@router.put("/products/{product_id}/inventory")
async def update_inventory(
    product_id: int,
    stock_quantity: int = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Quick update for stock levels"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(404, "Product not found")
        
    db_product.stock_quantity = stock_quantity
    db.commit()
    return {"message": "Inventory updated", "stock_quantity": stock_quantity}

# --- REPORTS & ANALYTICS ---

@router.get("/reports/summary")
async def get_reports_summary(db: Session = Depends(get_db)):
    """Aggregate Store Statistics for the Reports Page"""
    
    # 1. Total Revenue (Paid Orders only)
    revenue_query = db.query(func.sum(Order.total_amount)).filter(Order.payment_status == 'paid').scalar()
    total_revenue = float(revenue_query) if revenue_query else 0.0
    
    # 2. Total Orders
    total_orders = db.query(Order).count()
    
    # 3. Total Customers
    total_customers = db.query(User).count()
    
    # 4. Total Products (Active)
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # 5. Chart Data: Sales Last 7 Days
    from datetime import timedelta
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=6)
    
    sales_data = []
    labels = []
    
    # Iterate last 7 days to fill zeroes for empty days
    current_day = seven_days_ago
    while current_day <= today:
        day_start = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        daily_revenue = db.query(func.sum(Order.total_amount))\
            .filter(Order.payment_status == 'paid')\
            .filter(Order.created_at >= day_start, Order.created_at <= day_end)\
            .scalar() or 0.0
            
        sales_data.append(float(daily_revenue))
        labels.append(current_day.strftime("%a")) # Mon, Tue...
        current_day += timedelta(days=1)
        
    return {
        "revenue": total_revenue,
        "orders": total_orders,
        "customers": total_customers,
        "products": total_products,
        "chart": {
            "labels": labels,
            "data": sales_data
        }
    }

# --- DISCOUNT MANAGEMENT ---

from models.store import Discount
from schemas.store import Discount as DiscountSchema, DiscountCreate

@router.get("/discounts", response_model=List[DiscountSchema])
async def list_discounts(db: Session = Depends(get_db)):
    """List all discount codes"""
    return db.query(Discount).order_by(Discount.created_at.desc()).all()

@router.post("/discounts", response_model=DiscountSchema)
async def create_discount(discount: DiscountCreate, db: Session = Depends(get_db)):
    """Create a new discount code"""
    if db.query(Discount).filter(Discount.code == discount.code).first():
        raise HTTPException(400, "Discount code already exists")
    
    db_discount = Discount(**discount.dict())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

@router.delete("/discounts/{discount_id}")
async def delete_discount(discount_id: int, db: Session = Depends(get_db)):
    db_discount = db.query(Discount).filter(Discount.id == discount_id).first()
    if not db_discount:
        raise HTTPException(404, "Discount not found")
        
    db.delete(db_discount)
    db.commit()
    return {"message": "Discount deleted"}

# --- ADVANCED PAYMENTS MANAGEMENT ---

@router.get("/payments/status")
async def get_payment_status():
    """
    Real-time status check of the Payment Gateway (Stripe).
    Returns Balance, Mode, and Connection Status.
    """
    if not settings.stripe_secret_key:
        return {
            "connected": False,
            "mode": "Not Configured",
            "balance": {"available": 0.00, "pending": 0.00, "currency": "usd"}
        }

    try:
        stripe.api_key = settings.stripe_secret_key
        # Fetch Real Balance
        bal = stripe.Balance.retrieve()
        
        # Parse first available currency
        available = bal.available[0].amount / 100 if bal.available else 0
        pending = bal.pending[0].amount / 100 if bal.pending else 0
        currency = bal.available[0].currency if bal.available else "usd"

        return {
            "connected": True,
            "mode": "Live" if "live" in settings.stripe_secret_key else "Test",
            "balance": {
                "available": available,
                "pending": pending,
                "currency": currency.upper()
            }
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "mode": "Error",
            "balance": {"available": 0, "pending": 0, "currency": "usd"}
        }

@router.get("/payments/transactions")
async def get_payment_transactions(limit: int = 10):
    """
    Directly fetch recent transactions from Stripe for the ledger.
    """
    if not settings.stripe_secret_key:
        return []

    try:
        stripe.api_key = settings.stripe_secret_key
        charges = stripe.Charge.list(limit=limit)
        
        return [{
            "id": c.id,
            "amount": c.amount / 100,
            "currency": c.currency.upper(),
            "status": c.status, # succeeded, pending, failed
            "date": datetime.fromtimestamp(c.created),
            "receipt_url": c.receipt_url,
            "payment_method": c.payment_method_details.type if c.payment_method_details else "unknown",
            "customer_email": c.billing_details.email or "Unknown"
        } for c in charges.auto_paging_iter()]
    except Exception as e:
        print(f"Stripe Error: {e}")
        return []

# --- SHIPPING MANAGEMENT ---

from models.store import ShippingZone, ShippingRate
from schemas.store import ShippingZone as ShippingZoneSchema, ShippingZoneCreate, ShippingRateCreate

@router.get("/shipping/zones", response_model=List[ShippingZoneSchema])
async def list_shipping_zones(db: Session = Depends(get_db)):
    """List all shipping zones and their configured rates"""
    return db.query(ShippingZone).all()

@router.post("/shipping/zones", response_model=ShippingZoneSchema)
async def create_shipping_zone(zone: ShippingZoneCreate, db: Session = Depends(get_db)):
    """Create a new geographic zone (e.g. 'North America')"""
    db_zone = ShippingZone(name=zone.name, countries=zone.countries)
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    
    # Add initial rates if any (though usually done separately)
    for rate_data in zone.rates:
        db_rate = ShippingRate(**rate_data.dict(), zone_id=db_zone.id)
        db.add(db_rate)
    
    db.commit()
    db.refresh(db_zone)
    return db_zone

@router.post("/shipping/zones/{zone_id}/rates")
async def add_shipping_rate(
    zone_id: int, 
    rate: ShippingRateCreate, 
    db: Session = Depends(get_db)
):
    """Add a shipping method to a zone"""
    db_zone = db.query(ShippingZone).filter(ShippingZone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(404, "Zone not found")
        
    db_rate = ShippingRate(**rate.dict(), zone_id=zone_id)
    db.add(db_rate)
    db.commit()
    return {"message": "Rate added"}

@router.delete("/shipping/zones/{zone_id}")
async def delete_shipping_zone(zone_id: int, db: Session = Depends(get_db)):
    db_zone = db.query(ShippingZone).filter(ShippingZone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(404, "Zone not found")
        
    db.delete(db_zone)
    db.commit()
    return {"message": "Zone deleted"}
