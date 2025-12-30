from .base import *

# Use simple staticfiles storage for tests to avoid manifest errors
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
