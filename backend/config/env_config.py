"""
Environment configuration helper for ClientIQ.
Centralizes all environment variable handling.
"""

import os
from decouple import config


class Config:
    """Configuration class that handles all environment variables."""
    
    # Server Configuration
    HOST = config('HOST', default='localhost')
    PORT = config('PORT', default=8000, cast=int)
    DEBUG = config('DEBUG', default=True, cast=bool)
    SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
    
    # Domain Configuration
    MAIN_DOMAIN = config('MAIN_DOMAIN', default='localhost')
    PRODUCTION_DOMAIN = config('PRODUCTION_DOMAIN', default='clientiq.com')
    FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')
    
    # Database Configuration
    DATABASE_URL = config('DATABASE_URL', default='')
    DATABASE_NAME = config('DATABASE_NAME', default='clientiq_db')
    DATABASE_USER = config('DATABASE_USER', default='postgres')
    DATABASE_PASSWORD = config('DATABASE_PASSWORD', default='root')
    DATABASE_HOST = config('DATABASE_HOST', default='localhost')
    DATABASE_PORT = config('DATABASE_PORT', default=5432, cast=int)
    
    # Redis Configuration
    REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')
    REDIS_HOST = config('REDIS_HOST', default='localhost')
    REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
    
    # JWT Configuration
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='your-jwt-secret-key')
    JWT_ALGORITHM = config('JWT_ALGORITHM', default='HS256')
    JWT_ACCESS_TOKEN_LIFETIME = config('JWT_ACCESS_TOKEN_LIFETIME', default=3600, cast=int)
    JWT_REFRESH_TOKEN_LIFETIME = config('JWT_REFRESH_TOKEN_LIFETIME', default=86400, cast=int)
    
    # Email Configuration
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='ClientIQ Team <noreply@clientiq.com>')
    SALES_EMAIL = config('SALES_EMAIL', default='sales@clientiq.com')
    
    # Celery Configuration
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
    
    # API Configuration
    API_VERSION = config('API_VERSION', default='v1')
    BASE_URL = config('BASE_URL', default='http://localhost:8000')
    
    # CORS Configuration
    CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='')
    
    # Allowed Hosts
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1')
    
    # Logging
    LOG_LEVEL = config('LOG_LEVEL', default='INFO')
    
    @classmethod
    def get_allowed_hosts_list(cls):
        """Get ALLOWED_HOSTS as a list."""
        hosts = [host.strip() for host in cls.ALLOWED_HOSTS.split(',') if host.strip()]
        if cls.DEBUG:
            hosts.extend(['.localhost'])  # Allow all subdomains of localhost in development
        return hosts
    
    @classmethod
    def get_cors_allowed_origins_list(cls):
        """Get CORS_ALLOWED_ORIGINS as a list."""
        if cls.CORS_ALLOW_ALL_ORIGINS:
            return []
        return [origin.strip() for origin in cls.CORS_ALLOWED_ORIGINS.split(',') if origin.strip()]
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration."""
        if cls.DATABASE_URL and cls.DATABASE_URL.startswith('postgresql'):
            import dj_database_url
            return dj_database_url.parse(cls.DATABASE_URL)
        
        return {
            'ENGINE': 'django_tenants.postgresql_backend',
            'NAME': cls.DATABASE_NAME,
            'USER': cls.DATABASE_USER,
            'PASSWORD': cls.DATABASE_PASSWORD,
            'HOST': cls.DATABASE_HOST,
            'PORT': cls.DATABASE_PORT,
            'SCHEMA': 'public',
        }
