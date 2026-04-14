# Ecosystem Root Structure

```
ecosystem/                          # Main repository - "The Founder's Package"
│
├── docker-compose.yml               # Root orchestrator - deploys ALL services
├── docker-compose.override.yml      # Local development overrides
├── Dockerfile                       # Legacy - to be deprecated
├── nginx.conf                       # Root gateway - routes by domain to services
├── Makefile                         # CLI: make deploy-all, make deploy blog, etc.
├── .env                             # Root environment variables
├── .env.example                     # Template for founders
├── .gitignore
├── README.md                        # Main entry point documentation
│
├── .github/                         # GitHub Actions CI/CD
│   └── workflows/
│       └── deploy-all.yml           # Triggers all 6 service deploy workflows
│
├── docs/                            # Centralized documentation
│   ├── setup/                       # General setup guides
│   │   ├── backend-setup.md
│   │   ├── deployment_guide_mailing.md
│   │   ├── setup-guide.md
│   │   └── site-description.md
│   │
│   ├── admin/                       # Admin service docs (TBD)
│   ├── agent/                       # Agent service docs (TBD)
│   ├── blog/                        # Blog service docs (TBD)
│   ├── gigs/                        # Gigs service docs
│   │   ├── API_CHANGELOG.md
│   │   ├── ARCHITECTURE_OVERVIEW.md
│   │   ├── ATS_INTEGRATIONS.md
│   │   ├── AUTHENTICATION.md
│   │   ├── CLI.md
│   │   ├── COMPANY_SLUG_DIRECTORY.md
│   │   ├── DEPLOYMENT.md
│   │   ├── FAQ.md
│   │   ├── GLOSSARY.md
│   │   ├── PERFORMANCE_TUNING.md
│   │   ├── PLUGIN_ARCHITECTURE.md
│   │   ├── PRD_NEW_JOB_SOURCES.md
│   │   ├── ROADMAP.md
│   │   ├── SECURITY_GUIDELINES.md
│   │   └── UPGRADE_GUIDE.md
│   ├── mail/                        # Mail service docs (TBD)
│   ├── portfolio/                  # Portfolio service docs (TBD)
│   └── store/                      # Store service docs (TBD)
│
├── packages/                        # Shared packages for all services
│   ├── common/                     # Shared utilities (auth, JWT, fingerprinting)
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── index.ts
│   │       ├── auth/
│   │       ├── utils/
│   │       └── http/
│   │
│   └── config/                     # Shared environment/config handling
│       ├── package.json
│       └── src/
│           ├── index.ts
│           └── environments/
│
├── services/                       # All microservices
│   ├── admin/                      # Admin dashboard service
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── main.ts
│   │   │   ├── app.module.ts
│   │   │   ├── controllers/
│   │   │   ├── services/
│   │   │   ├── views/             # Admin HTML templates
│   │   │   └── static/             # Admin CSS, JS, images
│   │   ├── templates/              # Jinja2 templates (legacy - to move to src/)
│   │   ├── static/                 # Static assets (legacy)
│   │   ├── docs/                   # Links to docs/admin/
│   │   └── .github/workflows/
│   │       └── deploy.yml
│   │
│   ├── agent/                      # AI Agent service (TBD)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── main.ts
│   │   │   ├── database/           # Agent's own database
│   │   │   ├── controllers/
│   │   │   └── services/
│   │   └── .github/workflows/
│   │       ├── ci.yml              # Has tests
│   │       └── deploy.yml
│   │
│   ├── blog/                       # Blog service
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   └── src/
│   │       ├── main.ts
│   │       ├── database/           # Blog's own database
│   │       ├── controllers/
│   │       ├── services/
│   │       ├── templates/          # Jinja2 templates
│   │       └── static/             # CSS, JS, images
│   │   ├── templates/              # Jinja2 templates (legacy - to move to src/)
│   │   ├── static/                 # Static assets (legacy)
│   │   ├── docs/                   # Links to docs/blog/
│   │   └── .github/workflows/
│   │       ├── ci.yml              # Has tests
│   │       └── deploy.yml
│   │
│   ├── gigs/                       # Job intelligence engine
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   ├── nx.json
│   │   ├── nest-cli.json
│   │   ├── jest.config.js
│   │   └── src/
│   │       ├── main.ts
│   │       ├── database/           # Gigs own database
│   │       ├── apps/
│   │       │   ├── api/
│   │       │   ├── cli/
│   │       │   └── mcp/
│   │       ├── packages/
│   │       │   ├── analytics/
│   │       │   ├── common/
│   │       │   ├── models/
│   │       │   ├── plugin/
│   │       │   └── plugins/       # 170+ job source plugins
│   │       ├── data/
│   │       └── logs/
│   │   ├── docs/                   # Links to docs/gigs/
│   │   └── .github/workflows/
│   │       ├── ci.yml              # Has tests
│   │       └── deploy.yml
│   │
│   ├── mail/                       # Email/mailing service (TBD)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   └── src/
│   │       ├── main.ts
│   │       ├── database/           # Mail's own database
│   │       ├── controllers/
│   │       └── services/
│   │   └── .github/workflows/
│   │       ├── ci.yml              # Has tests
│   │       └── deploy.yml
│   │
│   ├── portfolio/                  # Portfolio showcase service (STATIC - no DB)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── package.json
│   │   └── src/
│   │       ├── main.ts
│   │       ├── index.html
│   │       ├── css/
│   │       ├── js/
│   │       ├── img/
│   │       └── fonts/
│   │   └── .github/workflows/
│   │       └── deploy.yml          # No CI (static site)
│   │
│   └── store/                      # E-commerce service
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── package.json
│       └── src/
│           ├── main.ts
│           ├── database/           # Store's own database
│           ├── controllers/
│           ├── services/
│           ├── templates/
│           └── static/
│       ├── templates/              # Jinja2 templates (legacy)
│       ├── static/                 # Static assets (legacy)
│       ├── docs/                   # Links to docs/store/
│       └── .github/workflows/
│           ├── ci.yml              # Has tests
│           └── deploy.yml
│
├── infrastructure/                 # Infrastructure as Code
│   ├── docker/
│   │   ├── docker-compose.yml     # Root services: postgres, redis, nginx
│   │   └── traefik/              # Reverse proxy config
│   │
│   ├── kubernetes/                 # K8s manifests (future)
│   │   ├── namespace.yml
│   │   ├── ingress.yml
│   │   └── services/
│   │
│   └── terraform/                  # Terraform configs (future)
│       ├── main.tf
│       └── variables.tf
│
└── plans/                          # Planning & specs
    ├── product_spec.md             # Overall product specification
    └── root.md                    # This file - ecosystem structure
```

## Databases (7 Total)

| Service   | Database Name     | Purpose                          |
|-----------|------------------|----------------------------------|
| Admin     | `admin_db`       | Shared resources: users, roles, settings, sessions |
| Agent     | `agent_db`       | Agent data, AI models, tasks    |
| Blog      | `blog_db`        | Posts, comments, authors, tags  |
| Gigs      | `gigs_db`        | Job listings, tracking, cache   |
| Mail      | `mail_db`        | Campaigns, subscribers, logs    |
| Portfolio | (none)           | Static site - no database       |
| Store     | `store_db`       | Products, orders, customers     |

## Service Ports Mapping

| Service   | Port | Domain                    |
|-----------|------|---------------------------|
| Admin     | 8001 | admin.nekwasar.com       |
| Agent     | 8002 | agent.nekwasar.com       |
| Blog      | 8003 | blog.nekwasar.com        |
| Gigs      | 8004 | gigs.nekwasar.com        |
| Mail      | 8005 | mail.nekwasar.com        |
| Portfolio | 8006 | nekwasar.com             |
| Store     | 8007 | store.nekwasar.com       |

## Shared Dependencies

- PostgreSQL (7 separate databases in infrastructure/docker/)
- Redis (for caching/sessions)
- Nginx (root nginx.conf as gateway)
- Common packages in /packages/
