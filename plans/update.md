# Update Checklist

## Phase 1: Infrastructure Setup

- [ ] Create `infrastructure/docker/docker-compose.yml` with PostgreSQL (7 databases), Redis, Nginx
- [ ] Create `infrastructure/docker/traefik/` configuration
- [ ] Update root `docker-compose.yml` to reference infrastructure and services

## Phase 2: Create Services Structure

- [ ] Move `BACKEND/` to `services/admin/` (convert to FastAPI/NestJS)
- [ ] Create `services/agent/` (new)
- [ ] Move `blog/` to `services/blog/` (convert to FastAPI/NestJS)
- [ ] Move `gigs/` to `services/gigs/`
- [ ] Create `services/mail/` (new)
- [ ] Move `portfolio/` to `services/portfolio/`
- [ ] Move `store/` to `services/store/` (convert to FastAPI/NestJS)

## Phase 3: Database Separation

- [ ] Create `services/admin/src/database/` with AdminUser, roles, settings models
- [ ] Create `services/agent/src/database/` with agent-specific models
- [ ] Create `services/blog/src/database/` with blog, post, comment, author models
- [ ] Create `services/gigs/src/database/` with job, tracking models
- [ ] Create `services/mail/src/database/` with campaign, subscriber models
- [ ] Create `services/store/src/database/` with product, order, customer models

## Phase 4: CI/CD Setup

- [ ] Create `services/admin/.github/workflows/deploy.yml`
- [ ] Create `services/agent/.github/workflows/ci.yml`
- [ ] Create `services/agent/.github/workflows/deploy.yml`
- [ ] Create `services/blog/.github/workflows/ci.yml`
- [ ] Create `services/blog/.github/workflows/deploy.yml`
- [ ] Move `gigs/.github/workflows/` to `services/gigs/.github/workflows/`
- [ ] Create `services/mail/.github/workflows/ci.yml`
- [ ] Create `services/mail/.github/workflows/deploy.yml`
- [ ] Create `services/portfolio/.github/workflows/deploy.yml`
- [ ] Create `services/store/.github/workflows/ci.yml`
- [ ] Create `services/store/.github/workflows/deploy.yml`
- [ ] Update root `.github/workflows/deploy-all.yml`

## Phase 5: Shared Packages

- [ ] Create `packages/common/` with auth, JWT, fingerprinting utilities
- [ ] Create `packages/config/` with environment handling

## Phase 6: Documentation

- [ ] Create `docs/admin/` documentation
- [ ] Create `docs/agent/` documentation
- [ ] Create `docs/blog/` documentation
- [ ] Move `docs/gigs/` to existing location
- [ ] Create `docs/mail/` documentation
- [ ] Create `docs/portfolio/` documentation
- [ ] Create `docs/store/` documentation

## Phase 7: Cleanup

- [ ] Remove root `Dockerfile` (legacy)
- [ ] Remove root `docker-compose.yml` (use infrastructure/ instead)
- [ ] Remove `packages/database/` from plan (not needed)
- [ ] Move all service folders to `services/`

## Phase 8: Testing & Deployment

- [ ] Test each service independently
- [ ] Test all services together via `docker-compose`
- [ ] Deploy to production
