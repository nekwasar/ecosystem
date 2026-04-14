# CDN Service Documentation

## Overview
The CDN Service provides file upload and delivery via Bunny.net integration.

## Technology Stack
- **Framework**: FastAPI (Python)
- **CDN Provider**: Bunny.net
- **Port**: 8006

## Features
- Direct upload to Bunny.net Storage
- CDN URL generation for fast delivery
- Local storage fallback when Bunny.net is not configured
- File management (upload, delete)

## API Endpoints
- `GET /health` - Health check with CDN status
- `POST /api/cdn/upload` - Upload file to CDN
- `DELETE /api/cdn/files?path={path}` - Delete file from CDN
- `GET /api/cdn/stats` - Get CDN configuration and stats

## Environment Variables
- `BUNNY_API_KEY` - Bunny.net API key
- `BUNNY_STORAGE_ZONE` - Bunny.net storage zone name
- `CDN_BASE_URL` - Your CDN domain (e.g., https://cdn.nekwasar.com)

## Setup Bunny.net
1. Create account at bunny.net
2. Create a Storage Zone
3. Get your API key from Bunny.net Dashboard
4. Configure your CDN domain (pull zone)

## Docker
```bash
docker build -t nekwasar-cdn services/cdn
docker run -d --name ecosystem_cdn -p 8006:8006 \
  -e BUNNY_API_KEY=your_api_key \
  -e BUNNY_STORAGE_ZONE=your_storage_zone \
  -e CDN_BASE_URL=https://cdn.nekwasar.com \
  nekwasar-cdn
```
