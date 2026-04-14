# Store Service Documentation

## Overview
The Store Service provides e-commerce functionality with products, orders, and categories.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Port**: 8004

## API Endpoints
- `GET /health` - Health check
- `GET /api/products` - List products
- `GET /api/products/{slug}` - Get product by slug
- `GET /api/categories` - List categories
- `POST /api/orders` - Create order

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string

## Docker
```bash
docker build -t nekwasar-store services/store
docker run -d --name ecosystem_store -p 8004:8004 nekwasar-store
```
