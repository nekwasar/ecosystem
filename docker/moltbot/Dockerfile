FROM python:3.10-slim

# ROBI'S BRAIN (Agent Runtime)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System Power (Git for updates, Curl for checks)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Agent Dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright (God-Tier scraping power)
RUN pip install playwright
RUN playwright install --with-deps chromium

# Setup ROBI's Rooms
RUN mkdir -p /app/workspace /app/config /app/skills

# Default Command: Keep ROBI alive and listening
CMD ["tail", "-f", "/dev/null"]
