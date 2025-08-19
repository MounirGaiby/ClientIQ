"""
Test settings for comprehensive testing.
Extends settings_simple with test-specific configurations.
"""

from .settings_simple import *
import os

# Test-specific database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable tenant functionality for testing
DATABASE_ROUTERS = []

# All apps for testing (without django_tenants)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Your apps
    'apps.platform',
    'apps.users',
    'apps.demo',
    'apps.authentication',
    'apps.common',
    'apps.permissions',
    'apps.tenant_permissions',
]

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# Uncomment to disable migrations for faster tests
# MIGRATION_MODULES = DisableMigrations()

# Test-specific settings
DEBUG = True
SECRET_KEY = 'test-secret-key-for-testing-only'

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache backend for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django_tenants': {
            'handlers': ['null'],
            'propagate': False,
        },
        'apps': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

# Test media settings
MEDIA_ROOT = '/tmp/test_media'
STATIC_ROOT = '/tmp/test_static'

# Celery settings for testing
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# DRF settings for testing
REST_FRAMEWORK.update({
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
})

# JWT settings for testing
from datetime import timedelta
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=1),
})

# Test-specific tenant settings
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'apps.users',
]

SHARED_APPS = [
    'django_tenants',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'apps.tenants',
    'apps.demo',
    'apps.platform',
    'apps.authentication',
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Test runner configuration (use default Django test runner for now)
# TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Coverage settings
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'venv', 'node_modules',
    '__pycache__', r'\.git', r'\.tox', r'\.coverage',
    'build', 'dist', r'\.egg-info',
]

# Disable CORS for testing
CORS_ALLOW_ALL_ORIGINS = True

# Disable CSRF for API testing
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Test file storage
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'
