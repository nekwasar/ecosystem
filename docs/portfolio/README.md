# Portfolio Service Documentation

## Overview
The Portfolio Service provides a personal portfolio website.

## Technology Stack
- **Framework**: Static HTML/Nginx
- **Port**: 80

## Docker
```bash
docker build -t nekwasar-portfolio services/portfolio
docker run -d --name ecosystem_portfolio -p 80:80 nekwasar-portfolio
```
