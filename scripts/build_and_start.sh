#!/bin/bash

set -e

echo "🚀 Building and starting DeepSecure ID system..."

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p infra/postgres-data
mkdir -p infra/redis-data
mkdir -p backend/uploads
mkdir -p backend/models
mkdir -p backend/logs

# Create self-signed certificates if they don't exist
if [ ! -f "certs/server.crt" ] || [ ! -f "certs/server.key" ]; then
    echo "🔐 Creating self-signed certificates..."
    mkdir -p certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout certs/server.key \
        -out certs/server.crt \
        -subj "/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check if backend is responding
echo "🔍 Checking backend health..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "Waiting for backend to be ready..."
    sleep 5
done

echo "✅ Backend is ready!"

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec backend alembic upgrade head

# Pre-seed data
echo "🌱 Pre-seeding database..."
bash scripts/preseed_data.sh

echo ""
echo "🎉 DeepSecure ID system is ready!"
echo ""
echo "📱 Frontend: https://localhost"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "👤 Default accounts:"
echo "   Admin: admin@local / adminpass"
echo "   User:  user@local / userpass"
echo ""
echo "🔍 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
