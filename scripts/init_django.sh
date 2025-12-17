#!/bin/bash
set -e

echo "🚀 Initializing Buildly CollabHub for production..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Clean Python cache to ensure fresh bytecode
echo "🧹 Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Set production settings if not already set
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-mysite.settings.production}

# Run Django makemigrations, migrate, and collectstatic
echo "📊 Running database migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo "📁 Collecting static files..."
python3 manage.py collectstatic --noinput

# Create admin user for Forge marketplace management
echo "👤 Creating admin user..."
python3 manage.py create_admin_user --skip-if-exists

# Initialize onboarding content for production
echo "🎯 Initializing onboarding content..."
python3 scripts/init_onboarding_data.py

echo "✅ Buildly CollabHub initialization complete!"
