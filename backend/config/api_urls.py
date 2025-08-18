"""
API URL configuration for ClientIQ.
"""
from django.urls import path, include

urlpatterns = [
    # Demo API endpoints (public schema)
    path('demo/', include('apps.demo.urls')),
    
    # Authentication endpoints
    path('auth/', include('apps.authentication.urls')),
    
    # Tenant management endpoints
    path('tenants/', include('apps.tenants.urls')),
    
    # User management endpoints (tenant-specific)
    path('users/', include('apps.users.urls')),
]
