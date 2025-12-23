#!/bin/bash
# Quick start script for Linux Voice AI Assistant

echo "🎙️  Linux Voice AI Assistant - Quick Start"
echo ""

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

echo "✅ Docker and Docker Compose found"
echo ""

# Allow X11 connections from Docker
echo "🔓 Allowing X11 connections from Docker..."
xhost +local:docker

echo ""
echo "🚀 Starting Linux Voice AI Assistant..."
echo ""

# Run with docker-compose
docker-compose up --build

# Cleanup on exit
echo ""
echo "🧹 Cleaning up..."
xhost -local:docker
