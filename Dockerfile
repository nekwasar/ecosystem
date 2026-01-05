FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY BACKEND/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn

# Copy entire project (needed for blog/portfolio/store templates and statics)
COPY . .

# Set working directory to where main.py is expected to run
WORKDIR /app/BACKEND/app

# Expose port
EXPOSE 8000

# Command to run for production
CMD ["gunicorn", "main:app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
