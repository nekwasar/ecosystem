# Docker Network Configuration

## Network Name
`ecosystem_network`

## Service Communication

All services communicate via Docker internal network using service names:

| Service | Internal URL | External Port |
|---------|-------------|---------------|
| PostgreSQL | postgres:5432 | 5432 |
| Redis | redis:6379 | 6379 |
| Nginx | nginx:80 | 80, 443 |
| Admin | admin:8001 | via nginx |
| Agent | agent:8002 | via nginx |
| Blog | blog:8003 | via nginx |
| Gigs | gigs:8004 | via nginx |
| Mail | mail:8005 | via nginx |
| Portfolio | portfolio:8006 | via nginx |
| Store | store:8007 | via nginx |

## Database Connection Strings

```bash
# Admin Service
postgresql://ecosystem:password@postgres:5432/admin_db

# Agent Service
postgresql://ecosystem:password@postgres:5432/agent_db

# Blog Service
postgresql://ecosystem:password@postgres:5432/blog_db

# Gigs Service
postgresql://ecosystem:password@postgres:5432/gigs_db

# Mail Service
postgresql://ecosystem:password@postgres:5432/mail_db

# Store Service
postgresql://ecosystem:password@postgres:5432/store_db
```

## Redis Connection

```bash
redis://redis:6379
```

## Testing Connections

### Test PostgreSQL
```bash
# From host machine
docker exec -it ecosystem_postgres psql -U ecosystem -d postgres

# Inside container network
docker exec -it ecosystem_postgres psql -U ecosystem -h postgres -d admin_db
```

### Test Redis
```bash
docker exec -it ecosystem_redis redis-cli
```

### Test Service-to-Service
```bash
# From admin container to postgres
docker exec -it ecosystem_admin ping postgres

# From blog container to redis
docker exec -it ecosystem_blog ping redis
```

## Firewall Rules

If testing from local machine:
```bash
# Allow PostgreSQL
sudo ufw allow 5432/tcp

# Allow Redis (if needed)
sudo ufw allow 6379/tcp
```
