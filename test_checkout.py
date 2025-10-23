#!/usr/bin/env python
"""
Test script to debug the checkout process
"""
import os
import sys
import django
import requests
import json

# Setup Django environment
sys.path.insert(0, '/Users/greglind/Projects/buildly/collabhub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings.dev')
django.setup()

from django.contrib.auth.models import User
from forge.models import ForgeApp
from django.test import Client
from django.urls import reverse

def test_checkout_api():
    """Test the checkout API endpoint"""
    print("=" * 50)
    print("Testing Checkout API")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'password': 'testpass123'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Get the babblebeaver app
    try:
        app = ForgeApp.objects.get(slug='babblebeaver')
        print(f"Found app: {app.name} (${app.price_dollars})")
        print(f"App ID: {app.id}")
        print(f"Price cents: {app.price_cents}")
        print(f"Is published: {app.is_published}")
    except ForgeApp.DoesNotExist:
        print("ERROR: babblebeaver app not found!")
        return
    
    # Create Django test client
    client = Client()
    
    # Login the user
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {login_success}")
    
    # Test the checkout API endpoint
    url = '/marketplace/api/purchases/create_checkout/'
    data = {
        'forge_app_id': str(app.id)
    }
    
    print(f"Making POST request to: {url}")
    print(f"Data: {data}")
    
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json'
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.items())}")
    
    try:
        response_data = response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response content: {response.content.decode()}")
    
    # Test the checkout page directly
    print("\n" + "=" * 50)
    print("Testing Checkout Page")
    print("=" * 50)
    
    checkout_url = f'/marketplace/checkout/{app.slug}/'
    print(f"Testing checkout page: {checkout_url}")
    
    page_response = client.get(checkout_url)
    print(f"Checkout page status: {page_response.status_code}")
    
    if page_response.status_code != 200:
        print(f"Checkout page error: {page_response.content.decode()}")
    else:
        print("Checkout page loaded successfully")

if __name__ == '__main__':
    test_checkout_api()