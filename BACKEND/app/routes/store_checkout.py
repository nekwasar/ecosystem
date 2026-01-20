from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import get_db
from models.store import Order, OrderItem, Product, OrderStatus, BillingScheme
from schemas.store import Product as ProductSchema # Reuse for strict typing if needed
import stripe
from core.config import settings

router = APIRouter()

# --- CART LOGIC ---
# In a real enterprise app, Cart is usually a Redis session or a dedicated DB table 'Cart'.
# For this V1 without user auth on every guest, we will define the "Cart" as a JSON payload 
# passed from the frontend (Client-Side Cart) for validation during Checkout Intent.
# This simplifies backend state management immensely.

# --- CHECKOUT ---

@router.post("/intent")
async def create_payment_intent(
    request: Request, # Added Request to read cookies
    items: list[dict] = Body(...), 
    currency: str = Body("usd"),
    db: Session = Depends(get_db)
):
    """
    The Smart Checkout Brain:
    1. Validates prices from DB (Never trust client).
    2. Calculates Tax (Stripe Tax).
    3. Handles Mixed Bags (Subscription + One-Time).
    4. Returns Client Secret.
    """
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(500, "Payment gateway configuration missing")
    
    # Identify User
    from jose import jwt
    user_id = None
    user_email = None
    
    token = request.cookies.get("store_session")
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            # Fetch email for receipt
            from models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if user: user_email = user.email
        except:
            pass # Invalid session -> Guest Checkout

    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    line_items = []
    has_subscription = False
    
    # 1. Validate Items & Build Line Items
    for item in items:
        product = db.query(Product).filter(Product.id == item['product_id']).first()
        if not product:
            continue
            
        if product.billing_scheme == BillingScheme.RECURRING:
            has_subscription = True
            # For Subscriptions, we need the Stripe Price ID
            if not product.stripe_price_id:
                 raise HTTPException(400, f"Product {product.name} is missing Stripe configuration")
            
            line_items.append({
                "price": product.stripe_price_id,
                "quantity": item.get('quantity', 1),
            })
        else:
            # One-Time Purchase
            # We create a price-data object on the fly to ensure security
            line_items.append({
                "price_data": {
                    "currency": currency,
                    "unit_amount": int(product.price * 100), # Convert to cents
                    "product_data": {
                        "name": product.name,
                        "images": [img.file_url for img in product.images[:1]],
                        "metadata": {"db_product_id": product.id}
                    },
                    "tax_behavior": "exclusive", # Stripe Tax
                },
                "quantity": item.get('quantity', 1),
            })

    # 2. Create Session
    try:
        mode = "subscription" if has_subscription else "payment"
        
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode=mode,
            payment_method_types=["card"],
            success_url=f"{settings.DOMAIN}/store/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.DOMAIN}/store/cart",
            automatic_tax={"enabled": True}, # STRIPE TAX ENABLED
            
            # User Linking
            customer_email=user_email, # Pre-fill email field in Stripe
            client_reference_id=str(user_id) if user_id else None,
            metadata={
                "user_id": str(user_id) if user_id else "guest",
                "has_subscription": str(has_subscription).lower()
            }
        )
        
        return {"url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(400, f"Stripe Error: {str(e)}")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Async Handler for Payment Success.
    This is where we actually fulfill the order (email link, transfer domain, etc).
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
         raise HTTPException(400, "Invalid signature")
         
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # TODO: handle_order_fulfillment(session)
        pass
        
    return {"status": "success"}
