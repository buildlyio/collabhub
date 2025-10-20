#!/bin/bash

# Standalone Admin User Creation Script
# This script creates an admin superuser for Buildly CollabHub

set -e  # Exit on any error

echo "👤 Buildly CollabHub Admin User Setup"
echo "====================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

# Check if Django settings are configured
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-mysite.settings.production}
echo "⚙️  Using Django settings: $DJANGO_SETTINGS_MODULE"

# Check if admin user already exists
ADMIN_EXISTS=$(python manage.py shell -c "
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='admin')
    print('yes' if user.is_superuser else 'regular')
except User.DoesNotExist:
    print('no')
" 2>/dev/null)

echo "📊 Current admin status: $ADMIN_EXISTS"

if [ "$ADMIN_EXISTS" = "yes" ]; then
    echo ""
    echo "ℹ️  Admin superuser already exists."
    echo "   To update or reset password, use:"
    echo "   python manage.py create_admin_user"
    echo ""
    
    # Show existing admin info
    echo "Current admin user info:"
    python manage.py shell -c "
from django.contrib.auth.models import User
admin = User.objects.get(username='admin')
print(f'  Username: {admin.username}')
print(f'  Email: {admin.email}')
print(f'  Superuser: {admin.is_superuser}')
print(f'  Staff: {admin.is_staff}')
print(f'  Active: {admin.is_active}')
"
    
elif [ "$ADMIN_EXISTS" = "regular" ]; then
    echo ""
    echo "⚠️  Regular 'admin' user exists but is not superuser."
    echo "   Upgrading to superuser..."
    python manage.py create_admin_user
    
else
    echo ""
    echo "🆕 Creating new admin superuser..."
    
    # Check if password is provided via environment
    if [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
        echo "🔐 Using password from DJANGO_ADMIN_PASSWORD environment variable"
        python manage.py create_admin_user --password "$DJANGO_ADMIN_PASSWORD"
    else
        echo "🔐 Generating secure password..."
        python manage.py create_admin_user
    fi
fi

echo ""
echo "🌐 Admin Interface Access:"
echo "   URL: /admin/"
echo "   Forge Management: /admin/forge/"

echo ""
echo "💡 Usage Examples:"
echo "   # Create/update with custom password"
echo "   python manage.py create_admin_user --password mypassword"
echo ""
echo "   # Create with environment variable"
echo "   export DJANGO_ADMIN_PASSWORD=mypassword"
echo "   python manage.py create_admin_user --password \"\$DJANGO_ADMIN_PASSWORD\""
echo ""
echo "   # Create admin as labs customer (for testing discounts)"
echo "   python manage.py create_admin_user --labs-customer"

echo ""
echo "✅ Admin user setup complete!"