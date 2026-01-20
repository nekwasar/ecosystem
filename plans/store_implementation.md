# Enterprise Store Implementation Plan

## Executive Summary
This document outlines the comprehensive plan to build a scalable, "enterprise-level" e-commerce store for NekwasaR. The system will support diverse product lifecycles (one-time buys, subscriptions, high-ticket asset transfers) and feature a tiered access system for sensitive listings.

## 1. Database Architecture (Schema Redesign)

We will implement a relational schema that supports diverse product lifecycles and "Private Listings".

### 1.1 Products & Catalog
- **Products**:
    - Basics: `slug`, `sku`, `price`, `sale_price`.
    - Types: `digital_download` (files), `license_key` (software), `physical` (shipping), `transfer_service` (domains, apps), `subscription` (access plans).
    - Billing: `billing_scheme` (one_time or recurring), `interval` (month/year).
    - Privacy: `is_private_listing` (Boolean) - hides sensitive stats/price unless approved.
    - Media: Support for Mixed Gallery (Images + Video Previews).
- **ProductCategories**: Hierarchical categorization.
- **ProductAccessRequests**: For vetting high-ticket buyers (LinkedIn/Stripe ID).

### 1.2 Sales & Orders
- **Carts**: Persistent carts.
- **Orders**:
    - Statuses: `pending_payment`, `processing`, `completed`, `cancelled`, `transfer_pending`.
    - Support for mixed bags (buying 1 ebook + 1 subscription in same cart).
- **OrderMessages**: Secure chat for manual asset handover.

## 2. Backend API Development (FastAPI)

### 2.1 Storefront & Access Control
- `GET /api/store/products/{slug}`:
    - Logic to show "teaser" vs "full" data based on `ProductAccessRequest` status.
- `POST /api/store/products/{id}/request_access`:
    - Trigger manual admin review OR optional Stripe Identity session.

### 2.2 Cart & Checkout
- **Unified Checkout**: Logic to split One-Time vs Recurring items if needed (Stripe Checkout handles this natively now).
- `POST /api/store/checkout/intent`:
    - Creates Stripe checkout session.
    - Enables `tax_id_collection` (Stripe Tax).
    - Checks Radar rules implicitly.

### 2.3 Order Management & Handover
- `GET /api/store/orders/{id}/chat`: Fetch secure messages.
- `POST /api/store/orders/{id}/chat`: Send credential/transfer details securely.

### 2.4 Admin API
- **Manager**: Full CRUD including Subscription Plan setup (Price ID, Interval).
- **Vetting**: Dashboard to review Access Requests and Identity Verification results.
- **Fulfillment**: Chat interface for `transfer_pending` orders.

## 3. Frontend Implementation (Storefront)

A dynamic SPA-like experience within the Jinja2 templates.

### 3.1 Key Pages
- **Product Details**:
    - **Visuals**: Auto-playing video previews.
    - **The Gate**: "Request Access" button for Private Listings.
    - **Pricing**: Dynamic display ("$49" or "$10/mo").
- **User Dashboard**:
    - **My Orders**: History of one-time purchases.
    - **Subscriptions**: Manage active plans (Cancel/Upgrade).
    - **Private Assets**: Secure chat for domain transfers.

## 4. Workflows

### 4.1 Subscription (The Recurring Path)
1. User buys "Template Access Pass ($19/mo)".
2. Payment Success.
3. Stripe Webhook -> `subscription.created`.
4. System grants "Pro" role or access specific resources.
5. Monthly recurring charges handled by Stripe automatically.

### 4.2 High-Ticket Asset Transfer (The Vetted Path)
1. User sees "Gojo.xyz" (Private Listing).
2. User requests access.
3. **Optional**: System triggers Stripe Identity (Upload Passsport).
4. **Admin** approves request after review.
5. User pays $$$ via Stripe Invoice or Checkout.
6. Order Status -> `transfer_pending`.
7. **Secure Chat** opens for domain handover.

## 5. Implementation Phases

1.  **Phase 1: Foundation (Database Models)**
    -   Create complex Product (incl. billing fields), Order, and AccessRequest models.
    -   Migration/Update DB.

2.  **Phase 2: Admin Vetting & Management**
    -   Build the "Add Product" wizard (Video, Privacy, Subscription settings).
    -   Build the "Access Request" approval queue.

3.  **Phase 3: Storefront Logic**
    -   Implement public/private view logic.
    -   Cart & Checkout API (handling mixed billing).

4.  **Phase 4: Payments & Security**
    -   Stripe Integration (Tax, Radar, Identity, Subscriptions).
    -   Secure Chat implementation.

## Next Steps for User
Approve this plan to begin **Phase 1: Foundation**.
