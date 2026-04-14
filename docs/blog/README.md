# Blog Service Documentation

## Overview
The Blog Service provides blogging functionality with posts, comments, tags, and newsletter subscriptions.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Port**: 8003

## API Endpoints
- `GET /health` - Health check
- `GET /api/posts` - List posts
- `GET /api/posts/{slug}` - Get post by slug
- `POST /api/comments` - Create comment
- `POST /api/newsletter/subscribe` - Subscribe to newsletter

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string

## Docker
```bash
docker build -t nekwasar-blog services/blog
docker run -d --name ecosystem_blog -p 8003:8003 nekwasar-blog
```
