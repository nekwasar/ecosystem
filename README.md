# 🌌 NekwasaR Platform - Microservices Architecture

Welcome to the **NekwasaR Hub**, a high-performance, multi-domain microservices ecosystem designed for the "N•Gen Era."

## 🏗️ Architecture Overview

This platform uses a **microservices architecture** with 7 independent services:

| Service | Port | Technology | Description |
|---------|------|------------|-------------|
| Admin | 8001 | Python/FastAPI | Administrative panel |
| Agent | 8002 | Python/FastAPI | AI agent service |
| Blog | 8003 | Python/FastAPI | Blog platform |
| Store | 8004 | Python/FastAPI | E-commerce store |
| CDN | 8006 | Python/FastAPI | CDN with Bunny.net |
| Portfolio | 80 | Static/Nginx | Personal portfolio |
| Gigs | 3000 | Node.js/NestJS | Job board |

> **Note**: Email services handled by aapanel at mail.nekwasar.com

## 🚀 Quick Start

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Individual Service
```bash
# Build and run a specific service
cd services/<service-name>
docker build -t nekwasar-<service> .
docker run -d -p <port>:<port> nekwasar-<service>
```

## 📂 Project Structure

```
.
├── services/
│   ├── admin/       # Admin service
│   ├── agent/       # AI Agent service
│   ├── blog/        # Blog service
│   ├── store/       # E-commerce service
│   ├── cdn/        # CDN service
│   ├── portfolio/   # Portfolio service
│   └── gigs/       # Gigs service
├── packages/        # Shared packages
├── infrastructure/  # Docker infrastructure
├── docs/           # Service documentation
└── .github/        # CI/CD workflows
```

## 🛠️ Technology Stack

- **Backend**: Python FastAPI, Node.js NestJS
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **CDN**: Bunny.net
- **Reverse Proxy**: Nginx
- **Containerization**: Docker

## 📈 Key Features

- **Microservices**: Each service is independent and scalable
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Docker**: Complete containerization with docker-compose
- **Monitoring**: Health check endpoints on all services

## 🔧 Environment Variables

Required for each service:
- `DATABASE_URL` - PostgreSQL connection string

Agent service additionally requires:
- `OPENAI_API_KEY` - OpenAI API key

CDN service requires:
- `BUNNY_API_KEY` - Bunny.net API key
- `BUNNY_STORAGE_ZONE` - Bunny.net storage zone

## 📝 Documentation

See `/docs` directory for individual service documentation:
- `/docs/admin/README.md`
- `/docs/agent/README.md`
- `/docs/blog/README.md`
- `/docs/store/README.md`
- `/docs/portfolio/README.md`
- `/docs/cdn/README.md`

## 🚦 API Endpoints

All services expose a health check endpoint:
```
GET /health
```

---

*Built for the next generation of innovators. © 2026 NekwasaR.*
