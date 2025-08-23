from .base import *
import os
from os.path import join, normpath

# Use SQLite database for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

# Optional: Scope settings to access user repositories and issues
SOCIAL_AUTH_GITHUB_SCOPE = ['repo', 'user']  # Scopes to access private repositories and user data
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://collab.buildly.io/bounties'

# Use HTTPS for redirect URIs if applicable
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True  # Set this to True if you're using HTTPS