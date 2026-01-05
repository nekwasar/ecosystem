# 🌌 NekwasaR Platform

Welcome to the **NekwasaR Hub**, a high-performance, multi-domain ecosystem designed for the "N•Gen Era." This platform serves as the central engine for Nekwasa R. Ucheokoye's digital presence, encompassing a professional portfolio, a dynamic blog, and a high-conversion store.

## 🚀 Projects Overview

The platform is divided into three primary functional domains:

1.  **Portfolio (`/portfolio`)**: A premium, GSAP-powered showcase of tech innovation and milestones.
2.  **Blog (`/blog`)**: A robust, SEO-optimized publishing platform featuring dynamic templates, unique view tracking, and community engagement.
3.  **Store (`/store`)**: An e-commerce gateway for premium tech products and consultations.

## 🛠️ Technology Stack

### Backend Engine (The Core)
- **Framework**: FastAPI (Python 3.13+)
- **Database**: PostgreSQL (Production) / SQLite (Local-friendly)
- **ORM**: SQLAlchemy 2.0
- **Security**: JWT Authentication, Bcrypt hashing, Device Fingerprinting
- **Tracking**: Unique View Tracking with 24h cooldown/deduplication

### Frontend & Aesthetics
- **Core**: Vanilla JS, HTML5, CSS3
- **Animations**: GSAP (GreenSock), ScrollTrigger, Lenis (Smooth Scroll)
- **Icons**: Phosphor Icons, Font Awesome
- **Theming**: Integrated Dark/Light mode with local persistence

## 📂 Project Structure

```text
.
├── BACKEND/          # FastAPI application (Routes, Models, Schemas)
├── blog/             # Blog frontend & Jinja2 Templates
├── portfolio/        # Milestone & Portfolio frontend
├── store/            # Storefront interface
├── docker/           # Deployment & Containerization configurations
└── docs/             # Technical guides and API documentation
```

## 🚥 Quick Start

1.  **Setup Backend**:
    ```bash
    cd BACKEND/app
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```
2.  **Interactive Docs**: Visit `http://localhost:8000/docs` to explore the API.
3.  **Configurations**: Copy `.env.example` to `.env` and configure your DATABASE_URL.

## 📈 Key Features

- **Unique Engagement**: Fingerprint-based likes, comments, and views to ensure authentic metrics.
- **Admin Dashboard**: Advanced CMS with WYSIWYG editing, workflow management, and analytics.
- **Enhanced Security**: Two-Factor Authentication (MFA/TOTP), account lockout protection, and role-based access control.
- **Newsletter & Automation**: Integrated Brevo mailing system for manual campaigns and targeted automation workflows.
- **SEO First**: Dynamic meta-tags, OpenGraph support, and high-performance Core Web Vitals.

---
*Built for the next generation of innovators. © 2026 NekwasaR.*
