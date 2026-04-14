# Deployment Guide

## Docker Compose (recommended)

```bash
# 1. Copy and edit environment variables
cp .env.example .env

# 2. Build and start
docker compose up -d

# 3. Verify health
curl http://localhost:3001/health
```

## Standalone Docker

```bash
docker build -t ever-jobs-api .
docker run -d \
  --name ever-jobs-api \
  -p 3001:3001 \
  --env-file .env \
  ever-jobs-api
```

## Development (Docker)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This mounts your source code for hot-reload and enables debug logging.

## Development (Local)

```bash
npm install
npm run start:dev
```

## Kubernetes (basic example)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ever-jobs-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ever-jobs-api
  template:
    metadata:
      labels:
        app: ever-jobs-api
    spec:
      containers:
        - name: api
          image: ever-jobs-api:latest
          ports:
            - containerPort: 3001
          envFrom:
            - configMapRef:
                name: ever-jobs-config
          livenessProbe:
            httpGet:
              path: /health
              port: 3001
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ping
              port: 3001
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: ever-jobs-api
spec:
  selector:
    app: ever-jobs-api
  ports:
    - port: 80
      targetPort: 3001
  type: LoadBalancer
```

## Environment Variables

See [`.env.example`](.env.example) for all configurable options.
