#!/bin/bash
# Quick setup script for local Docker development

echo "🐟 Setting up Fishing Directory for local development..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Create backend config if it doesn't exist
if [ ! -f "backend/api/config.php" ]; then
    echo "📝 Creating backend/api/config.php from example..."
    cp backend/api/config.example.php backend/api/config.php

    # Update for Docker
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/define('DB_HOST', 'localhost');/define('DB_HOST', 'mysql');/" backend/api/config.php
        sed -i '' "s/define('DB_PASS', 'your_password_here');/define('DB_PASS', 'fishing_password');/" backend/api/config.php
    else
        # Linux
        sed -i "s/define('DB_HOST', 'localhost');/define('DB_HOST', 'mysql');/" backend/api/config.php
        sed -i "s/define('DB_PASS', 'your_password_here');/define('DB_PASS', 'fishing_password');/" backend/api/config.php
    fi
    echo "   ✓ backend/api/config.php created with Docker credentials"
else
    echo "   ✓ backend/api/config.php already exists"
fi

# Start Docker containers
echo ""
echo "🐳 Starting Docker containers..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ Setup complete! Your services are available at:"
echo ""
echo "   🌐 Frontend:    http://localhost:4321"
echo "   🔌 API:         http://localhost:8000/api"
echo "   💾 phpMyAdmin:  http://localhost:8080"
echo "   🗄️  MySQL:       localhost:3306"
echo ""
echo "📝 To import data:"
echo "   cd data-pipeline"
echo "   python -m venv venv"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   pip install -r requirements.txt"
echo "   cd adapters"
echo "   python texas_lakes_adapter.py"
echo ""
echo "📚 Documentation: See docs/ folder or README.md"
echo ""
