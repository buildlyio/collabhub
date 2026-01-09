"""
API Key Helper Functions for CollabHub <-> Labs Integration

The APIKey model is defined in onboarding/models.py
This file contains helper functions for API key verification.
"""
from django.conf import settings


def get_labs_api_key():
    """Get the API key for calling Labs API"""
    # First try environment variable
    key = getattr(settings, 'LABS_API_KEY', None)
    if key:
        return key
    return None


def verify_inbound_request(request):
    """
    Verify an incoming API request from a partner.
    
    Checks for API key in:
    1. X-API-Key header
    2. Authorization: Bearer header
    3. api_key query parameter
    """
    from onboarding.models import APIKey
    
    # Check X-API-Key header
    api_key = request.headers.get('X-API-Key')
    
    # Check Authorization header
    if not api_key:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
    
    # Check query parameter
    if not api_key:
        api_key = request.GET.get('api_key')
    
    if not api_key:
        return None, "No API key provided"
    
    verified_key = APIKey.verify_key(api_key)
    if not verified_key:
        return None, "Invalid or inactive API key"
    
    return verified_key, None
