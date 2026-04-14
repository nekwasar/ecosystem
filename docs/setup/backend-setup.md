# 🧠 Backend Architecture & Technical Deep Dive

This document outlines the modular architecture of the NekwasaR Backend Engine.

## 🏛️ Modular Design Pattern

The application is structured for high scalability and maintainability, separating concerns into distinct directories.

### 1. Route Layer (`BACKEND/app/routes/`)
Each functional area has its own router dedicated to logic:
- `blogs.py`: Core publishing engine, view registration, and stat synchronization.
- `auth.py`: JWT generation, admin registration, and session management.
- `contacts.py`: Form submission and read/unread status management.
- `search.py`: High-speed content lookup.
- `newsletter.py`: Subscriber management and campaign triggers.
- `analytics.py`: Internal metric tracking and engagement trends.
- `admin.py`: Template rendering for the SPA-style management interface.

### 2. Model Layer (`BACKEND/app/models/`)
Structured SQLAlchemy models for data persistence:
- `blog.py`: Contains `BlogPost`, `BlogComment`, `BlogLike`, and `BlogView`.
- `user.py`: Admin user credentials and permissions.
- `contact.py`: Message storage and metadata.

### 3. Schema Layer (`BACKEND/app/schemas/`)
Pydantic models for data validation and API documentation:
- Modular schema files mapped to models.
- Centralized exports in `__init__.py`.

---

## 🛰️ Engagement & Tracking Engine

One of the most advanced features of the platform is the **Unique Engagement Tracking**.

### View Deduplication Logic
The `POST /api/blogs/{id}/view` endpoint follows this workflow:
1.  **Incoming Payload**: Receives a `fingerprint` from the client.
2.  **DB Lookup**: Checks `BlogView` table for `blog_post_id` + `fingerprint` where `expires_at > now()`.
3.  **Action**:
    - If found: Returns current stats without incrementing.
    - If not found: Increments `BlogPost.view_count` by 1 and registers a new `BlogView` with a 24h expiration.

---

## 🎨 Admin Integration Logic

The backend supports a dynamic, SPA-based admin editor.
- **Template Sanitization**: The system includes logic to strip editor artifacts (overlays, edit-wrappers, `contenteditable` attributes) before saving to the database.
- **Dynamic CSS/JS Injection**: Templates are rendered with specific admin styles injected into the `<head>` dynamically via the `admin_router`.

---

## ⚡ Performance Optimization

- **Database Dependency Injection**: Uses FastAPI's `Depends(get_db)` to ensure connections are automatically closed and returned to the pool.
- **JSON Compatibility**: Database models use SQLAlchemy's `JSON` type with fallback logic for both PostgreSQL and SQLite.
- **CORS Handling**: Intelligent allowed origin management in `core/config.py`.

---
*Technical Reference | Last Updated: 2026-01-01*