#!/bin/bash
# Docker Setup Script for Linux Voice AI with Ollama

set -e

echo "=========================================="
echo "Linux Voice AI - Docker Setup with Ollama"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Allow X11 connections from Docker
echo "🔓 Allowing X11 connections..."
xhost +local:docker

# Check if Ollama is running on host (port 11434)
if lsof -i :11434 > /dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":11434 "; then
    echo ""
    echo "⚠️  WARNING: Ollama is already running on host (port 11434)"
    echo "   Docker needs this port for the containerized Ollama."
    echo ""
    echo "   Please stop the host Ollama first:"
    echo "   sudo pkill ollama"
    echo ""
    echo "   Or if you prefer to use host Ollama instead of Docker:"
    echo "   1. Edit docker-compose.yml and remove the 'ollama' service"
    echo "   2. The voice assistant will use your host Ollama automatically"
    echo ""
    read -p "   Stop host Ollama now? (requires sudo) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo pkill ollama || true
        sleep 2
        echo "✅ Host Ollama stopped"
    else
        echo "❌ Cannot proceed with Docker Ollama while host Ollama is running."
        echo "   Exiting..."
        exit 1
    fi
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama is not responding. Checking logs..."
    docker-compose logs ollama
    exit 1
fi

echo "✅ Ollama is running!"

# Pull the functiongemma model
echo "📥 Pulling functiongemma:270m model (this may take a few minutes)..."
docker exec ollama ollama pull functiongemma:270m

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "🎙️  To view logs:"
echo "   docker-compose logs -f voice-assistant"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart:"
echo "   docker-compose restart"
echo ""
