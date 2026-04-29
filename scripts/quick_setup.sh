#!/bin/bash
# Quick setup script for Ancira Intelligence Dashboard
# This automates the initial database and platform setup

set -e  # Exit on error

echo "🚀 Ancira Intelligence Dashboard - Quick Setup"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend/app/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "❌ PostgreSQL client (psql) is required but not installed."; exit 1; }
command -v redis-cli >/dev/null 2>&1 || { echo "❌ Redis is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"
echo ""

# Check Redis connection
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   sudo systemctl start redis"
    echo "   OR"
    echo "   brew services start redis"
    exit 1
fi
echo "✅ Redis is running"
echo ""

# Prompt for database credentials
read -p "Enter PostgreSQL database name [ancira_intel]: " DB_NAME
DB_NAME=${DB_NAME:-ancira_intel}

read -p "Enter PostgreSQL username [ancira_user]: " DB_USER
DB_USER=${DB_USER:-ancira_user}

read -sp "Enter PostgreSQL password: " DB_PASS
echo ""

read -p "Enter PostgreSQL host [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

# Test database connection
export PGPASSWORD=$DB_PASS
if ! psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ Cannot connect to database. Please check credentials."
    echo "   To create the database, run:"
    echo "   sudo -u postgres psql"
    echo "   CREATE DATABASE $DB_NAME;"
    echo "   CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
    echo "   GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    exit 1
fi
echo "✅ Database connection successful"
echo ""

# Generate encryption key
echo "🔑 Generating encryption key..."
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "✅ Encryption key generated"
echo ""

# Generate secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Create .env file
echo "📝 Creating backend/.env file..."
cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@$DB_HOST:5432/$DB_NAME
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=$ENCRYPTION_KEY

# Application
APP_NAME="Ancira Competitive Intelligence Dashboard"
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=development

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Scraping
SCRAPE_VDP_LIMIT=3
SCRAPE_TIMEOUT_SECONDS=30
PLAYWRIGHT_HEADLESS=True

# OpenAI
DEFAULT_OPENAI_MODEL=gpt-5.4-mini-2026-03-17

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ancira-intel/app.log

# Initial Admin
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_EMAIL=admin@anciragroup.com
INITIAL_ADMIN_PASSWORD=ChangeMe123!
EOF

echo "✅ .env file created"
echo ""

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "🎭 Installing Playwright browsers..."
playwright install chromium

echo "🗄️  Running database migrations..."
alembic upgrade head

echo ""
echo "✅ Backend setup complete!"
echo ""

# Deactivate venv
deactivate
cd ..

# Frontend setup
echo "⚛️  Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies (this may take a few minutes)..."
    npm install
else
    echo "✅ npm dependencies already installed"
fi

cd ..

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend:"
echo "   cd backend && source venv/bin/activate"
echo "   python app/main.py"
echo ""
echo "2. Start Celery worker (in another terminal):"
echo "   cd backend && source venv/bin/activate"
echo "   celery -A app.tasks.celery_app worker --loglevel=info"
echo ""
echo "3. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:3000 and login:"
echo "   Username: admin"
echo "   Password: ChangeMe123!"
echo ""
echo "📖 For detailed testing instructions, see: END_TO_END_TEST.md"
echo ""
