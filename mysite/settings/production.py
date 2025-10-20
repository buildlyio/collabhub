from .base import *
import os
from os.path import join, normpath

# Use MySQL database for production with environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'defaultdb'),
        'USER': os.environ.get('DB_USER', 'doadmin'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),  # Must be set via environment variable
        'HOST': os.environ.get('DB_HOST', 'db-mysql-nyc3-40163-do-user-2508039-0.m.db.ondigitalocean.com'),
        'PORT': os.environ.get('DB_PORT', '25060'),
        'OPTIONS': {
            'sql_mode': 'traditional',
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'ssl': {'ssl-mode': 'REQUIRED'}
        }
    }
}

DEBUG = True

# ALLOWED_HOSTS = ['squid-app-sejn2.ondigitalocean.app', '127.0.0.1', '[::1]','punchlist.buildly.io','collab.buildly.io','market.buildly.io','localhost:3000']
try:
    ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')
except KeyError:
    ALLOWED_HOSTS = ['squid-app-sejn2.ondigitalocean.app', '127.0.0.1', '[::1]','punchlist.buildly.io','collab.buildly.io','market.buildly.io','localhost']

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = ALLOWED_HOSTS

# Removed import of local settings as it could not be resolved


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # new
DEFAULT_FROM_EMAIL = "admin@buildly.io"
EMAIL_HOST = "smtp.sendgrid.net"  # new
EMAIL_HOST_USER = "apikey"  # new
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_PASSWORD")  # new
EMAIL_PORT = 587  # new
EMAIL_USE_TLS = True  # new

AWS_STORAGE_BUCKET_NAME = 'collab'
AWS_ACCESS_KEY_ID = 'DO00MW9V6QPPJKVCGHYA'
AWS_SECRET_ACCESS_KEY = os.environ.get("SPACES_SECRET")
AWS_S3_CUSTOM_DOMAIN = 'cms-static.nyc3.digitaloceanspaces.com' + "/" + AWS_STORAGE_BUCKET_NAME
AWS_S3_ENDPOINT_URL  = 'https://cms-static.nyc3.digitaloceanspaces.com'


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_LOCATION}/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

AWS_DEFAULT_ACL = 'public-read'

SENDGRID_API_KEY = os.environ.get("SENDGRID")

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

YELP_API_KEY = os.environ.get('YELP_API_KEY')

# GitHub OAuth keys
SOCIAL_AUTH_GITHUB_KEY = os.environ.get('GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('GITHUB_SECRET')

# GitHub API token for Forge marketplace operations
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN')

# Forge marketplace settings
FORGE_MARKETPLACE_ORG = 'buildly-marketplace'
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://collab.buildly.io')

# Optional: Scope settings to access user repositories and issues
SOCIAL_AUTH_GITHUB_SCOPE = ['repo', 'user']  # Scopes to access private repositories and user data
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://collab.buildly.io/bounties'

# Use HTTPS for redirect URIs if applicable
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True  # Set this to True if you're using HTTPS

# Forge Marketplace Settings
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# GitHub API for repository validation
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN')

# Forge marketplace organization
FORGE_MARKETPLACE_ORG = os.environ.get('FORGE_MARKETPLACE_ORG', 'buildly-marketplace')

# Frontend URL for payment redirects
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://collab.buildly.io')