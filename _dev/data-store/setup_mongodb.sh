#!/bin/bash

# Setup script for MongoDB local development

set -e

echo "🚀 Setting up MongoDB for local development..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    
    # Check if MongoDB container already exists
    if docker ps -a --format '{{.Names}}' | grep -q "^mongodb$"; then
        echo "📦 MongoDB container exists"
        
        # Check if it's running
        if docker ps --format '{{.Names}}' | grep -q "^mongodb$"; then
            echo "✅ MongoDB container is already running"
        else
            echo "🔄 Starting existing MongoDB container..."
            docker start mongodb
            sleep 2
            echo "✅ MongoDB container started"
        fi
    else
        echo "📦 Creating new MongoDB container..."
        docker run -d \
            --name mongodb \
            -p 27017:27017 \
            -v mongodb_data:/data/db \
            mongo:latest
        
        echo "⏳ Waiting for MongoDB to be ready..."
        sleep 5
        echo "✅ MongoDB container created and started"
    fi
    
    echo ""
    echo "✅ MongoDB is running at: mongodb://localhost:27017"
    echo ""
    echo "To connect:"
    echo "  Connection string: mongodb://localhost:27017"
    echo "  Database: trainer_data (or any name you choose)"
    echo ""
    echo "To stop MongoDB:"
    echo "  docker stop mongodb"
    echo ""
    echo "To start MongoDB again:"
    echo "  docker start mongodb"
    echo ""
    echo "To remove MongoDB (and data):"
    echo "  docker stop mongodb && docker rm mongodb && docker volume rm mongodb_data"
    
else
    echo "❌ Docker not found"
    echo ""
    echo "Please install Docker:"
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo ""
    echo "Or install MongoDB manually:"
    echo "  https://www.mongodb.com/try/download/community"
    echo ""
    echo "Then start MongoDB:"
    echo "  mongod --dbpath /path/to/data"
fi

