#!/bin/bash

# Buildly Marketplace Import Script
# This script imports all repositories from buildly-marketplace GitHub organization
# as Forge products at $49 each

set -e  # Exit on any error

echo "🚀 Buildly Marketplace Import Script"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

# Check if GitHub token is set
if [ -z "$GITHUB_API_TOKEN" ]; then
    echo "❌ Error: GITHUB_API_TOKEN environment variable not set."
    echo "   Please set your GitHub API token:"
    echo "   export GITHUB_API_TOKEN=your_token_here"
    exit 1
fi

echo "✅ GitHub token found"
echo "📂 Working directory: $(pwd)"

# Run migrations first if needed
echo ""
echo "🔄 Checking database migrations..."
python manage.py showmigrations forge 2>/dev/null || {
    echo "⚠️  Forge migrations not found. Creating migrations..."
    python manage.py makemigrations forge
    echo "🔄 Applying migrations..."
    python manage.py migrate forge
}

# Check if migrations are up to date
if python manage.py showmigrations forge | grep -q "\[ \]"; then
    echo "🔄 Applying pending migrations..."
    python manage.py migrate forge
else
    echo "✅ Database migrations up to date"
fi

# Ensure admin user exists for marketplace management
echo "👤 Setting up admin user..."
python manage.py create_admin_user --skip-if-exists

# Show current app count
CURRENT_COUNT=$(python manage.py shell -c "from forge.models import ForgeApp; print(ForgeApp.objects.count())")
echo "📊 Current Forge apps in database: $CURRENT_COUNT"

echo ""
echo "🔍 Starting repository import..."
echo "   Organization: buildly-marketplace"
echo "   Price per app: \$49.00"
echo "   Target deployment: Docker containers"

# Run the import command
python manage.py import_marketplace_repos \
    --price-cents 4900 \
    --skip-existing \
    --validate

# Show final count
FINAL_COUNT=$(python manage.py shell -c "from forge.models import ForgeApp; print(ForgeApp.objects.count())")
IMPORTED_COUNT=$((FINAL_COUNT - CURRENT_COUNT))

echo ""
echo "🎉 Import completed successfully!"
echo "   Apps imported: $IMPORTED_COUNT"
echo "   Total apps: $FINAL_COUNT"
echo "   Total marketplace value: \$$(($FINAL_COUNT * 49))"

echo ""
echo "🔗 Next steps:"
echo "   1. Review apps in Django admin: /admin/forge/"
echo "   2. Test API endpoints: /forge/api/apps/"
echo "   3. Update app descriptions and screenshots as needed"

echo ""
echo "💡 Useful commands:"
echo "   # List all apps"
echo "   python manage.py shell -c \"from forge.models import ForgeApp; [print(f'{app.name} - \${app.price_cents/100}') for app in ForgeApp.objects.all()]\""
echo ""
echo "   # Validate all repositories"
echo "   python manage.py validate_forge_repos --published-only"
echo ""
echo "   # Create test data"
echo "   python manage.py create_forge_test_data --users 3 --apps 5"

echo ""
echo "✨ Buildly Marketplace is ready!"