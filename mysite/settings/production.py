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

DEBUG = False

# GitHub Error Reporting Configuration
GITHUB_ERROR_REPO = os.environ.get('GITHUB_ERROR_REPO', 'greglind/collabhub')  # Format: owner/repo
GITHUB_ERROR_TOKEN = os.environ.get('GITHUB_ERROR_TOKEN', '')  # GitHub personal access token

# ALLOWED_HOSTS = ['squid-app-sejn2.ondigitalocean.app', '127.0.0.1', '[::1]','punchlist.buildly.io','collab.buildly.io','market.buildly.io','localhost:3000']
try:
    ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')
except KeyError:
    ALLOWED_HOSTS = ['squid-app-sejn2.ondigitalocean.app', '127.0.0.1', '[::1]','punchlist.buildly.io','collab.buildly.io','market.buildly.io','localhost']

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = ALLOWED_HOSTS

# Removed import of local settings as it could not be resolved


# Email Configuration - MailerSend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "admin@buildly.io")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.mailersend.net")
EMAIL_HOST_USER = os.environ.get("MAILERSEND_SMTP_USERNAME")
EMAIL_HOST_PASSWORD = os.environ.get("MAILERSEND_SMTP_PASSWORD")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[Buildly Labs] ")

# Admin notification recipients
ADMINS = [
    ('Buildly Admin', 'admin@buildly.io'),
]
MANAGERS = ADMINS

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

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')

YELP_API_KEY = os.environ.get('YELP_API_KEY')

# GitHub OAuth keys
SOCIAL_AUTH_GITHUB_KEY = os.environ.get('GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('GITHUB_SECRET')

# GitHub OAuth and API settings
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN')
SOCIAL_AUTH_GITHUB_SCOPE = ['repo', 'user']  # Scopes to access private repositories and user data
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://collab.buildly.io/bounties'
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True  # Use HTTPS for redirect URIs

# Forge Marketplace Settings
FORGE_MARKETPLACE_ORG = os.environ.get('FORGE_MARKETPLACE_ORG', 'buildly-marketplace')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://collab.buildly.io')

# Stripe Payment Configuration (https://docs.stripe.com/keys)
# Only need these three keys according to current Stripe documentation:
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')          # sk_live_... or sk_test_...
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY') # pk_live_... or pk_test_...  
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')   # whsec_...

# Django Logging Configuration
# Captures all errors and sends them to stdout/stderr which DigitalOcean captures
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'collabhub': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'collabhub.errors': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'collabhub.views': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}