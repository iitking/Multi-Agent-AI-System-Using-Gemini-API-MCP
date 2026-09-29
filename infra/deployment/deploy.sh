#!/usr/bin/env bash
# Enterprise Multi-Agent Deployment Script
set -e

echo "=== Deploying Enterprise Multi-Agent AI System ==="

# Check environment variables
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
else
  echo "Warning: .env not found, using .env.example"
  cp .env.example .env
fi

# Build and launch Docker Compose services
echo "Building and launching containers via docker-compose..."
docker compose down || true
docker compose build
docker compose up -d

echo "=== Verifying Health Endpoints ==="
sleep 5

curl -f http://localhost:8000/health || echo "Backend starting up..."

echo ""
echo "=== Multi-Agent System Ready ==="
echo "• Dashboard: http://localhost:3000"
echo "• FastAPI Backend & Docs: http://localhost:8000/docs"
echo "• n8n Workflow Automation: http://localhost:5678"
