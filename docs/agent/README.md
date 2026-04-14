# Agent Service Documentation

## Overview
The Agent Service provides AI-powered agent functionality using OpenAI.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Port**: 8002
- **AI**: OpenAI API

## API Endpoints
- `GET /health` - Health check
- `POST /api/agent/chat` - Chat with AI agent

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key

## Docker
```bash
docker build -t nekwasar-agent services/agent
docker run -d --name ecosystem_agent -p 8002:8002 nekwasar-agent
```
