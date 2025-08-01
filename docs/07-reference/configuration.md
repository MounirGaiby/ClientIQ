# 📖 Configuration Reference

Complete reference for ClientIQ configuration options, environment variables, and system settings.

## 🔧 Environment Variables

### Core Django Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SETTINGS_MODULE` | Django settings module | `config.settings.local` | ✅ |
| `SECRET_KEY` | Django secret key for cryptographic signing | - | ✅ |
| `DEBUG` | Enable debug mode | `False` | ❌ |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost` | ✅ |

**Example:**
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Complete database connection string | - | ✅ |
| `DATABASE_NAME` | Database name | `clientiq` | ❌ |
| `DATABASE_USER` | Database username | `clientiq` | ❌ |
| `DATABASE_PASSWORD` | Database password | - | ✅ |
| `DATABASE_HOST` | Database host | `localhost` | ❌ |
| `DATABASE_PORT` | Database port | `5432` | ❌ |

**Example:**
```bash
# Using DATABASE_URL (recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/clientiq

# Or using individual variables
DATABASE_NAME=clientiq_production
DATABASE_USER=clientiq_prod
DATABASE_PASSWORD=super-secure-password
DATABASE_HOST=db.example.com
DATABASE_PORT=5432
```

### Redis Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Complete Redis connection string | `redis://localhost:6379/0` | ❌ |
| `REDIS_HOST` | Redis host | `localhost` | ❌ |
| `REDIS_PORT` | Redis port | `6379` | ❌ |
| `REDIS_DB` | Redis database number | `0` | ❌ |
| `REDIS_PASSWORD` | Redis password | - | ❌ |

**Example:**
```bash
# Using REDIS_URL (recommended)
REDIS_URL=redis://username:password@redis.example.com:6379/0

# Or using individual variables
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis-password
```

### Email Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `EMAIL_BACKEND` | Email backend class | `django.core.mail.backends.smtp.EmailBackend` | ❌ |
| `EMAIL_HOST` | SMTP server host | - | ✅ |
| `EMAIL_PORT` | SMTP server port | `587` | ❌ |
| `EMAIL_HOST_USER` | SMTP username | - | ✅ |
| `EMAIL_HOST_PASSWORD` | SMTP password | - | ✅ |
| `EMAIL_USE_TLS` | Use TLS encryption | `True` | ❌ |
| `EMAIL_USE_SSL` | Use SSL encryption | `False` | ❌ |
| `DEFAULT_FROM_EMAIL` | Default sender email | `noreply@clientiq.com` | ❌ |

**Example:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=ClientIQ <noreply@yourdomain.com>
```

### File Storage (AWS S3)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AWS_ACCESS_KEY_ID` | AWS access key | - | ❌ |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | ❌ |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name | - | ❌ |
| `AWS_S3_REGION_NAME` | AWS region | `us-east-1` | ❌ |
| `AWS_S3_CUSTOM_DOMAIN` | Custom S3 domain | - | ❌ |
| `AWS_DEFAULT_ACL` | Default file ACL | `private` | ❌ |

**Example:**
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=clientiq-files
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=cdn.yourdomain.com
AWS_DEFAULT_ACL=private
```

### Security Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECURE_SSL_REDIRECT` | Force HTTPS redirect | `False` | ❌ |
| `SECURE_PROXY_SSL_HEADER` | Proxy SSL header | - | ❌ |
| `SECURE_HSTS_SECONDS` | HSTS max age | `0` | ❌ |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | HSTS include subdomains | `False` | ❌ |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `False` | ❌ |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `False` | ❌ |

**Production Security Example:**
```bash
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### JWT Authentication

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `JWT_SECRET_KEY` | JWT signing key | Uses `SECRET_KEY` | ❌ |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access token lifetime (minutes) | `15` | ❌ |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (days) | `7` | ❌ |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | ❌ |

**Example:**
```bash
JWT_SECRET_KEY=different-secret-for-jwt-tokens
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7
JWT_ALGORITHM=HS256
```

### Celery Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CELERY_BROKER_URL` | Celery broker URL | Uses `REDIS_URL` | ❌ |
| `CELERY_RESULT_BACKEND` | Celery result backend | Uses `REDIS_URL` | ❌ |
| `CELERY_TASK_ALWAYS_EAGER` | Execute tasks synchronously | `False` | ❌ |
| `CELERY_WORKER_CONCURRENCY` | Worker concurrency | `4` | ❌ |

**Example:**
```bash
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_ALWAYS_EAGER=False
CELERY_WORKER_CONCURRENCY=4
```

## ⚙️ Django Settings Reference

### Settings Files Structure

```
config/
├── settings/
│   ├── __init__.py          # Default settings import
│   ├── base.py              # Base settings for all environments
│   ├── local.py             # Local development settings
│   ├── testing.py           # Test environment settings
│   └── production.py        # Production settings
```

### Base Settings (`config/settings/base.py`)

**Core Configuration:**
```python
import os
from pathlib import Path
from decouple import config

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'django_tenants',
    'corsheaders',
    'django_filters',
]

LOCAL_APPS = [
    'apps.common',
    'apps.tenants',
    'apps.users',
    'apps.authentication',
    'apps.permissions',
    'apps.subscriptions',
    'apps.payments',
    'apps.translations',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.tenants.middleware.TenantIsolationMiddleware',
    'apps.common.middleware.AuditMiddleware',
]

# URL configuration
ROOT_URLCONF = 'config.urls'
```

**Database Configuration:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DATABASE_NAME', default='clientiq'),
        'USER': config('DATABASE_USER', default='clientiq'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
        'OPTIONS': {
            'options': '-c default_transaction_isolation=serializable'
        },
    }
}

# Tenant configuration
DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)

TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

SHARED_APPS = [
    'django_tenants',
    'apps.tenants',
    'apps.common',
]

TENANT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'apps.users',
    'apps.authentication',
    'apps.permissions',
    'apps.subscriptions',
    'apps.payments',
    'apps.translations',
]
```

### Local Development Settings (`config/settings/local.py`)

```python
from .base import *

# Debug
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.localhost']

# Database
DATABASES['default'].update({
    'NAME': config('DATABASE_NAME', default='clientiq_dev'),
    'USER': config('DATABASE_USER', default='clientiq'),
    'PASSWORD': config('DATABASE_PASSWORD', default='dev_password'),
})

# Cache (dummy for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email (console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Debug toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }

# CORS (allow all for development)
CORS_ALLOW_ALL_ORIGINS = True
```

### Production Settings (`config/settings/production.py`)

```python
from .base import *

# Security
DEBUG = False
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Sessions
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Cache (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# File storage (AWS S3)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
AWS_DEFAULT_ACL = 'private'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/clientiq/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

## 🔌 API Configuration

### Django REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
}
```

### JWT Configuration

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=15, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}
```

### CORS Configuration

```python
# Development
CORS_ALLOW_ALL_ORIGINS = True

# Production
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-tenant-id',
]
```

## 📊 Monitoring Configuration

### Sentry Error Tracking

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN', default=None),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float),
    send_default_pii=True,
    environment=config('ENVIRONMENT', default='development'),
)
```

### Health Check Configuration

```python
# apps/common/views.py
HEALTH_CHECK_CONFIG = {
    'database': {
        'enabled': True,
        'timeout': 5,
    },
    'cache': {
        'enabled': True,
        'timeout': 2,
    },
    'storage': {
        'enabled': True,
        'timeout': 10,
    },
    'celery': {
        'enabled': True,
        'timeout': 5,
    },
}
```

## 🐳 Docker Configuration

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgresql://clientiq:password@db:5432/clientiq
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: clientiq
      POSTGRES_USER: clientiq
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A config worker -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgresql://clientiq:password@db:5432/clientiq
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - media_volume:/app/media

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

## 📝 Management Commands Reference

### Built-in Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `migrate` | Apply database migrations | `python manage.py migrate` |
| `makemigrations` | Create new migrations | `python manage.py makemigrations [app_name]` |
| `collectstatic` | Collect static files | `python manage.py collectstatic` |
| `createsuperuser` | Create admin user | `python manage.py createsuperuser` |
| `runserver` | Start development server | `python manage.py runserver [port]` |
| `shell` | Open Django shell | `python manage.py shell` |
| `test` | Run tests | `python manage.py test [app_name]` |

### Custom Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `seed_db` | Populate database with sample data | `python manage.py seed_db [--mode MODE]` |
| `quickstart` | Quick project setup | `python manage.py quickstart` |

**Seed Database Command Options:**
```bash
# Modes
python manage.py seed_db --mode development  # Full development data
python manage.py seed_db --mode production   # Basic production data
python manage.py seed_db --mode minimal      # Minimal required data

# Options
python manage.py seed_db --tenants 5         # Number of tenants to create
python manage.py seed_db --users-per-tenant 10  # Users per tenant
python manage.py seed_db --clear-existing    # Clear existing data first
```

## 🔍 Performance Tuning

### Database Optimization

```python
# Connection pooling
DATABASES['default']['OPTIONS'].update({
    'MAX_CONNS': 20,
    'OPTIONS': {
        'MAX_CONNS': 20,
    }
})

# Query optimization
DATABASES['default']['OPTIONS'].update({
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
    'charset': 'utf8mb4',
})
```

### Cache Configuration

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'clientiq',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Session cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Static Files Optimization

```python
# Static files compression
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# Enable compression
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
```

---

This reference provides comprehensive configuration details for all aspects of ClientIQ deployment and operation. Use it as your go-to guide for environment setup and system configuration.
