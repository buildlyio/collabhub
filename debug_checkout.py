#!/usr/bin/env python
"""
Debug script for checkout issues in production
Run this to diagnose checkout problems
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/greglind/Projects/buildly/collabhub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.production')
django.setup()

from django.conf import settings
from forge.models import ForgeApp
import stripe

print("=== PRODUCTION CHECKOUT DIAGNOSTICS ===")
print()

# 1. Check Stripe Configuration
print("1. STRIPE CONFIGURATION:")
print(f"   STRIPE_API_KEY: {'SET' if getattr(settings, 'STRIPE_API_KEY', None) else 'NOT SET'}")
print(f"   STRIPE_PUBLISHABLE_KEY: {'SET' if getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None) else 'NOT SET'}")
print(f"   STRIPE_WEBHOOK_SECRET: {'SET' if getattr(settings, 'STRIPE_WEBHOOK_SECRET', None) else 'NOT SET'}")

if hasattr(settings, 'STRIPE_API_KEY') and settings.STRIPE_API_KEY:
    stripe.api_key = settings.STRIPE_API_KEY
    key_type = "LIVE" if settings.STRIPE_API_KEY.startswith('sk_live_') else "TEST"
    print(f"   Key Type: {key_type}")
    
    try:
        # Test Stripe connection
        account = stripe.Account.retrieve()
        print(f"   Stripe Connection: SUCCESS")
        print(f"   Account ID: {account.id}")
    except Exception as e:
        print(f"   Stripe Connection: FAILED - {str(e)}")
else:
    print("   Stripe Connection: NO API KEY")

print()

# 2. Check Frontend URL
print("2. FRONTEND URL:")
frontend_url = getattr(settings, 'FRONTEND_URL', 'NOT SET')
print(f"   FRONTEND_URL: {frontend_url}")
print()

# 3. Check App Data
print("3. APP DATA:")
try:
    app = ForgeApp.objects.get(slug='babblebeaver')
    print(f"   App Name: {app.name}")
    print(f"   App ID: {app.id}")
    print(f"   Price (cents): {app.price_cents}")
    print(f"   Price (dollars): ${app.price_dollars}")
    print(f"   Published: {app.is_published}")
except ForgeApp.DoesNotExist:
    print("   ERROR: Babblebeaver app not found!")
print()

# 4. Check Authentication Settings
print("4. AUTHENTICATION:")
auth_classes = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_AUTHENTICATION_CLASSES', [])
print(f"   REST Framework Auth Classes: {auth_classes}")
print()

# 5. Environment Variables Check
print("5. ENVIRONMENT VARIABLES:")
env_vars = [
    'STRIPE_API_KEY',
    'STRIPE_PUBLISHABLE_KEY', 
    'STRIPE_WEBHOOK_SECRET',
    'FRONTEND_URL',
    'DJANGO_SETTINGS_MODULE'
]

for var in env_vars:
    value = os.environ.get(var)
    if value:
        if 'STRIPE' in var and 'SECRET' in var:
            # Mask secret keys
            masked = f"{value[:8]}{'*' * (len(value) - 16)}{value[-8:]}" if len(value) > 16 else "SET"
            print(f"   {var}: {masked}")
        else:
            print(f"   {var}: {value}")
    else:
        print(f"   {var}: NOT SET")

print()
print("=== RECOMMENDATIONS ===")
print()

issues = []

if not getattr(settings, 'STRIPE_API_KEY', None):
    issues.append("- Set STRIPE_API_KEY environment variable")

if not getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None):
    issues.append("- Set STRIPE_PUBLISHABLE_KEY environment variable")

if frontend_url == 'NOT SET':
    issues.append("- Set FRONTEND_URL environment variable")

if hasattr(settings, 'STRIPE_API_KEY') and settings.STRIPE_API_KEY:
    if settings.STRIPE_API_KEY.startswith('sk_live_'):
        issues.append("- Using LIVE Stripe keys - ensure they are valid and active")
    elif settings.STRIPE_API_KEY.startswith('sk_test_'):
        issues.append("- Using TEST Stripe keys - good for development/testing")
    else:
        issues.append("- Stripe key format unrecognized")

if not auth_classes or 'rest_framework.authentication.SessionAuthentication' not in str(auth_classes):
    issues.append("- Add SessionAuthentication to REST_FRAMEWORK settings for web checkout")

if issues:
    for issue in issues:
        print(issue)
else:
    print("No obvious configuration issues found!")

print()
print("=== NEXT STEPS ===")
print("1. Check server logs for detailed error messages")
print("2. Verify Stripe dashboard shows the API key is active")  
print("3. Test with curl: curl -X POST -H 'Content-Type: application/json' -d '{\"forge_app_id\":\"APP_ID\"}' YOUR_DOMAIN/marketplace/api/purchases/create_checkout/")
print("4. Check browser network tab for full error response")