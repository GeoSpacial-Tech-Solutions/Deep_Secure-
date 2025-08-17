#!/bin/bash

echo "Pre-seeding DeepSecure ID database with initial data..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Create admin user
echo "Creating admin user..."
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@local",
    "password": "adminpass"
  }'

# Create regular user
echo "Creating regular user..."
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "email": "user@local",
    "password": "userpass"
  }'

# Get admin token and make user admin
echo "Making admin user admin..."
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=adminpass" | jq -r '.access_token')

if [ "$ADMIN_TOKEN" != "null" ] && [ "$ADMIN_TOKEN" != "" ]; then
    # Update admin user to be admin
    curl -X PUT "http://localhost:8000/api/auth/users/1" \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "is_admin": true
      }'
    
    echo "Admin user created and configured successfully!"
else
    echo "Failed to get admin token. Admin user may not have been created properly."
fi

echo "Pre-seeding completed!"
echo ""
echo "Default accounts:"
echo "Admin: admin@local / adminpass"
echo "User:  user@local / userpass"
echo ""
echo "You can now log in at http://localhost:8000/docs"
