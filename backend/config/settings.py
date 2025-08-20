"""
Django settings for ClientIQ multi-tenant application.
Proper configuration following django-tenants best practices.
"""

from pathlib import Path
import os
from decouple import config
from .env_config import Config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = Config.SECRET_KEY
DEBUG = Config.DEBUG

# Proper ALLOWED_HOSTS configuration for multi-tenancy
ALLOWED_HOSTS = Config.get_allowed_hosts_list()

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = Config.CORS_ALLOW_ALL_ORIGINS
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = Config.get_cors_allowed_origins_list()

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Database Configuration
DATABASES = {
    'default': Config.get_database_config()
}

from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)

# Proper ALLOWED_HOSTS configuration for multi-tenancy
if DEBUG:
    # Development: Allow localhost and all .localhost subdomains
    allowed_hosts_env = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',')]
    ALLOWED_HOSTS.extend(['.localhost'])  # Allow all subdomains of localhost
else:
    # Production: Set your actual domain
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# CORS Settings
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
else:
    cors_origins = config('CORS_ALLOWED_ORIGINS', default='')
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Database Configuration
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
    # Production/PostgreSQL with multi-tenancy
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    DATABASES['default']['ENGINE'] = 'django_tenants.postgresql_backend'
    USE_MULTI_TENANCY = True
else:
    # Development/SQLite - single tenant mode
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    USE_MULTI_TENANCY = False

# Multi-tenant App Configuration
if USE_MULTI_TENANCY:
    # Apps shared across all tenants (public schema)
    SHARED_APPS = [
        'django_tenants',  # Must be first for multi-tenant
        'apps.tenants',    # Tenant management
        'apps.demo',       # Demo requests (pre-tenant)
        'apps.platform',   # Platform admin users
        'apps.permissions', # Custom permissions & roles
        'apps.authentication', # Auth middleware & admin
        
        # Django core apps
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        
        # Third party
        'rest_framework',
        'rest_framework_simplejwt',
        'rest_framework_simplejwt.token_blacklist',
        'corsheaders',
    ]
    
    # Apps installed per tenant schema
    TENANT_APPS = [
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'apps.users',     # Tenant users
        'apps.contacts',  # Tenant data
    ]
    
    INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]
    
    # Multi-tenant models
    TENANT_MODEL = "tenants.Tenant"
    TENANT_DOMAIN_MODEL = "tenants.Domain"
    
    # Database routing
    DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']
    
    # Middleware with tenant detection
    MIDDLEWARE = [
        'django_tenants.middleware.main.TenantMainMiddleware',  # Must be first
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    # Platform admin users for public schema
    AUTH_USER_MODEL = 'platform.SuperUser'
    
else:
    # Single tenant mode (development)
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'rest_framework_simplejwt',
        'rest_framework_simplejwt.token_blacklist',
        'corsheaders',
        'apps.users',
        'apps.demo',
        'apps.contacts',
        'apps.permissions',
        'apps.authentication',
        'apps.tenants',
        'apps.platform',
    ]
    
    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    # Use custom user for development
    AUTH_USER_MODEL = 'users.CustomUser'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# JWT Configuration
from datetime import timedelta

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=Config.JWT_ACCESS_TOKEN_LIFETIME),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=Config.JWT_REFRESH_TOKEN_LIFETIME),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': Config.JWT_ALGORITHM,
    'SIGNING_KEY': Config.JWT_SECRET_KEY,
}

# Email Configuration
EMAIL_BACKEND = Config.EMAIL_BACKEND
if not DEBUG:
    EMAIL_HOST = Config.EMAIL_HOST
    EMAIL_PORT = Config.EMAIL_PORT
    EMAIL_USE_TLS = Config.EMAIL_USE_TLS
    EMAIL_HOST_USER = Config.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = Config.EMAIL_HOST_PASSWORD

DEFAULT_FROM_EMAIL = Config.DEFAULT_FROM_EMAIL

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': Config.LOG_LEVEL,
    },
    'loggers': {
        'django_tenants': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
