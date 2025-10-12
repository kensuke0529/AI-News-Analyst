#!/bin/bash

# AI News Analyst Deployment Script
# This script helps deploy the application using Docker

set -e  # Exit on any error

echo "🚀 AI News Analyst Deployment Script"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f config/env.example ]; then
        cp config/env.example .env
        echo "📝 Please edit .env file with your OpenAI API key and other settings."
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ config/env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "❌ Please set your OpenAI API key in the .env file."
    echo "   Edit .env and replace 'your_openai_api_key_here' with your actual API key."
    exit 1
fi

echo "✅ Environment configuration looks good!"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/vector_db
mkdir -p chroma_db

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose -f deployment/docker-compose.yml build

echo "🚀 Starting AI News Analyst..."
docker-compose -f deployment/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
if curl -f http://localhost:8002/ > /dev/null 2>&1; then
    echo "✅ Backend API is running at http://localhost:8002"
else
    echo "❌ Backend API is not responding"
fi

if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📱 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8002"
echo "   API Status: http://localhost:8002/api/status"
echo ""
echo "📊 Useful commands:"
echo "   View logs: docker-compose -f deployment/docker-compose.yml logs -f"
echo "   Stop services: docker-compose -f deployment/docker-compose.yml down"
echo "   Restart services: docker-compose -f deployment/docker-compose.yml restart"
echo "   Update application: docker-compose -f deployment/docker-compose.yml pull && docker-compose -f deployment/docker-compose.yml up -d"
echo ""
echo "🔧 To populate the news database, run:"
echo "   docker-compose -f deployment/docker-compose.yml exec ai-news-analyst python src/data_ingestion/extract_and_store.py"
