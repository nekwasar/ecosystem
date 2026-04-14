#!/bin/bash
# Test PostgreSQL Connection Script

set -e

echo "=========================================="
echo "PostgreSQL Connection Test"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Start PostgreSQL container
echo "Starting PostgreSQL container..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Test connection
echo "Testing connection..."
docker exec -it ecosystem_postgres pg_isready -U ecosystem

# List databases
echo "Listing databases..."
docker exec -it ecosystem_postgres psql -U ecosystem -l

echo "=========================================="
echo "Connection test complete!"
echo "=========================================="
