# Admin Service Documentation

## Overview
The Admin Service provides administrative functionality for the Nekwasar ecosystem.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Port**: 8001

## API Endpoints
- `GET /health` - Health check
- `POST /api/admin/*` - Admin endpoints

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string

## Docker
```bash
docker build -t nekwasar-admin services/admin
docker run -d --name ecosystem_admin -p 8001:8001 nekwasar-admin
```
