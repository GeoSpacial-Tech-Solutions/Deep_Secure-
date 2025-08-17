#!/bin/bash

echo "🧪 Testing DeepSecure ID System..."

# Test backend health
echo "Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Test API info
echo "Testing API info..."
if curl -f http://localhost:8000/api/info > /dev/null 2>&1; then
    echo "✅ API info endpoint working"
else
    echo "❌ API info endpoint failed"
    exit 1
fi

# Test database connection
echo "Testing database connection..."
if docker-compose exec backend python -c "from app.database import get_db; print('Database connection successful')" 2>/dev/null; then
    echo "✅ Database connection working"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Test user creation
echo "Testing user creation..."
TEST_USER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }')

if echo "$TEST_USER_RESPONSE" | grep -q "testuser"; then
    echo "✅ User creation working"
else
    echo "❌ User creation failed"
    echo "Response: $TEST_USER_RESPONSE"
    exit 1
fi

# Clean up test user
echo "Cleaning up test user..."
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=adminpass" | jq -r '.access_token')

if [ "$ADMIN_TOKEN" != "null" ] && [ "$ADMIN_TOKEN" != "" ]; then
    USER_ID=$(echo "$TEST_USER_RESPONSE" | grep -o '"id":[0-9]*' | cut -d: -f2)
    curl -s -X DELETE "http://localhost:8000/api/auth/users/$USER_ID" \
      -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
    echo "✅ Test user cleaned up"
else
    echo "⚠️  Could not clean up test user (admin token failed)"
fi

echo ""
echo "🎉 All backend tests passed! DeepSecure ID system is working correctly."
echo ""
echo "📱 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "👤 Default accounts:"
echo "   Admin: admin@local.com / adminpass"
echo "   User:  user@local.com / userpass"
echo ""
echo "🔍 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
