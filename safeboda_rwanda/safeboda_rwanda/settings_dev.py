"""
Development Settings Override
Use this for local development to bypass production requirements
"""
from .settings import *

# Override production settings for development
DEBUG = True
SECRET_KEY = 'dev-secret-key-not-for-production-use-only'
ALLOWED_HOSTS = ['*']

# Disable HTTPS requirements for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Use simpler cache backend for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'safeboda-dev-cache',
    }
}

# CORS for local development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
]
CORS_ALLOW_ALL_ORIGINS = True

# Development logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['safeboda']['level'] = 'DEBUG'

print("🚀 Development settings loaded - DEBUG mode enabled")
