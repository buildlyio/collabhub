#!/bin/bash

# Deployment Check Script
# This script performs pre-deployment checks to catch issues early

set -e

echo "🔍 Buildly Forge Deployment Check"
echo "================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

echo "📁 Working directory: $(pwd)"

# Check Python syntax
echo ""
echo "🐍 Checking Python syntax..."
python3 -m py_compile forge/*.py
python3 -m py_compile forge/management/commands/*.py
echo "✅ Python syntax check passed"

# Check Django configuration
echo ""
echo "⚙️  Checking Django configuration..."
python3 manage.py check --deploy
echo "✅ Django configuration check passed"

# Check imports
echo ""
echo "📦 Checking critical imports..."
python3 -c "
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.base')
django.setup()

# Test critical imports
try:
    from forge.models import ForgeApp, RepoValidation, Purchase, Entitlement, UserProfile
    print('✅ Forge models import OK')
except ImportError as e:
    print(f'❌ Forge models import failed: {e}')
    exit(1)

try:
    from forge.serializers import ForgeAppListSerializer
    print('✅ Forge serializers import OK')
except ImportError as e:
    print(f'❌ Forge serializers import failed: {e}')
    exit(1)

try:
    from forge.services import GitHubRepoValidationService
    print('✅ Forge services import OK')
except ImportError as e:
    print(f'❌ Forge services import failed: {e}')
    exit(1)

try:
    from forge.views import ForgeAppViewSet
    print('✅ Forge views import OK')
except ImportError as e:
    print(f'❌ Forge views import failed: {e}')
    exit(1)

try:
    import forge.urls
    print('✅ Forge URLs import OK')
except ImportError as e:
    print(f'❌ Forge URLs import failed: {e}')
    exit(1)
"

# Check migrations
echo ""
echo "🗃️  Checking migrations..."
if python3 manage.py showmigrations forge | grep -q "\[ \]"; then
    echo "⚠️  Pending migrations found for forge app"
    echo "   Run: python3 manage.py migrate forge"
else
    echo "✅ Forge migrations up to date"
fi

# Check required settings
echo ""
echo "⚙️  Checking required settings..."
python3 -c "
from django.conf import settings

# Check if forge is in INSTALLED_APPS
if 'forge' not in settings.INSTALLED_APPS:
    print('❌ forge not in INSTALLED_APPS')
    exit(1)
else:
    print('✅ forge in INSTALLED_APPS')

# Check DRF is installed
if 'rest_framework' not in settings.INSTALLED_APPS:
    print('❌ rest_framework not in INSTALLED_APPS')
    exit(1)
else:
    print('✅ rest_framework in INSTALLED_APPS')

print('✅ Required settings check passed')
"

# Check URL configuration
echo ""
echo "🔗 Checking URL configuration..."
python3 -c "
from django.conf import settings
from django.urls import reverse
from django.test.utils import override_settings
import os

# Import URLs to check for syntax errors
try:
    from mysite.urls import urlpatterns
    print('✅ Main URL configuration OK')
except Exception as e:
    print(f'❌ URL configuration error: {e}')
    exit(1)
"

echo ""
echo "🎉 All deployment checks passed!"
echo ""
echo "📋 Deployment Summary:"
echo "   • Python syntax: ✅ OK"
echo "   • Django config: ✅ OK"
echo "   • Module imports: ✅ OK"
echo "   • URL routing: ✅ OK"
echo "   • Settings: ✅ OK"
echo ""
echo "🚀 Ready for deployment!"
echo ""
echo "💡 Next steps:"
echo "   1. Commit and push changes"
echo "   2. Deploy to buildly.io platform"
echo "   3. Run migrations in production"
echo "   4. Import marketplace apps"