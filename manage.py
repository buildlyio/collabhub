#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Check if DJANGO_SETTINGS_MODULE is already set
    if os.environ.get("DJANGO_SETTINGS_MODULE"):
        # Use whatever is explicitly set
        pass
    else:
        # Auto-detect environment based on production indicators
        # If any of these env vars are set, we're likely in production
        production_indicators = [
            'DB_HOST',      # Database host is set
            'DB_PASSWORD',  # Database password is set
            'ALLOWED_HOSTS',  # Allowed hosts configured
            'MAILERSEND_SMTP_PASSWORD',  # Email configured
        ]
        
        is_production = any(os.environ.get(var) for var in production_indicators)
        
        if is_production:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.production")
        else:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
