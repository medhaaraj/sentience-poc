#!/bin/bash

# Sentience POC Setup Script
# This script sets up the entire POC environment

set -e  # Exit on error

echo "🚀 Sentience POC Setup"
echo "====================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ All prerequisites met"
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p backend
mkdir -p db
mkdir -p telemetry
mkdir -p scripts
mkdir -p frontend

echo "✅ Directories created"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install requests > /dev/null 2>&1
echo "✅ Python dependencies installed"
echo ""

# Generate telemetry logs
echo "📊 Generating simulated SWG logs..."
if [ -f scripts/generate_logs.py ]; then
    python3 scripts/generate_logs.py
else
    echo "⚠️  Log generator not found. Please add scripts/generate_logs.py"
fi
echo ""

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d --build

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if backend is ready
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ Backend is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend failed to start"
    docker-compose logs backend
    exit 1
fi

echo ""

# Ingest telemetry
echo "📥 Ingesting telemetry logs..."
if [ -f scripts/ingest_logs.py ]; then
    python3 scripts/ingest_logs.py
else
    echo "⚠️  Ingestion script not found. Please add scripts/ingest_logs.py"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "🎯 Access the dashboard:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart"
echo ""
echo "📝 To regenerate data:"
echo "   python3 scripts/generate_logs.py"
echo "   python3 scripts/ingest_logs.py"
echo ""