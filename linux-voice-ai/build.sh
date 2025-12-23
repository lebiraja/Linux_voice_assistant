#!/bin/bash
# Build and run script for Linux Voice AI Assistant

set -e

echo "🚀 Building Linux Voice AI Assistant..."

# Build Docker image
docker-compose build

echo "✅ Build complete!"
echo ""
echo "To run the assistant:"
echo "  docker-compose up"
echo ""
echo "To run in detached mode:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop:"
echo "  docker-compose down"
