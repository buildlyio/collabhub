from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4w$$of)udb)qv8=vs^5vy#8%9+kk73x0u$de0dxg2xl+@s^v1g'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar",]

INTERNAL_IPS = [
    "localhost",
    "127.0.0.1",
]

try:
    from .local import *
except ImportError:
    pass

OPENAI_API_KEY = "asdfghjkl1234567890"
GOOGLE_PLACES_API_KEY = "AIzaSyDxlz70Pll-cl3e5G0ayzAZJ284282veOg"
YELP_API_KEY = "YOUR_YELP_API_KEY"

# labs auth
LABS_TOKEN_URL = os.environ.get('LABS_TOKEN_URL', 'https://labs-api.buildly.dev')
LABS_USERNAME = ""
LABS_PASSWORD = ""
"""
LABS_USERNAME = "superuser"
LABS_PASSWORD = "somepassword"
"""
LABS_CLIENT_ID = "someclientid"
LABS_CLIENT_SECRET = "password2025"