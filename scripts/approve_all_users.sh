#!/bin/bash

# Quick User Approval Script
# This script approves all pending users and creates missing profiles

set -e

echo "👤 Buildly User Approval Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django project root."
    exit 1
fi

echo "📊 Checking current user approval status..."

# Show current status
python manage.py approve_users --dry-run

echo ""
echo "🔧 Fixing approval issues..."

# Approve all users and create missing profiles
python manage.py approve_users --auto-approve --create-missing

echo ""
echo "✅ User approval complete!"
echo ""
echo "💡 What this script did:"
echo "   • Approved all existing TeamMember profiles"
echo "   • Created TeamMember profiles for users without them"
echo "   • Created Forge profiles for marketplace access"
echo "   • Set all new profiles to approved status"
echo ""
echo "🌐 Users can now access:"
echo "   • Dashboard: /onboarding/dashboard/"
echo "   • Forge Marketplace: /forge/api/apps/"
echo "   • Admin Interface: /admin/ (staff users only)"