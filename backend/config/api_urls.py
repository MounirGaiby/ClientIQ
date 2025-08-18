"""
API URL configuration for ClientIQ.
"""
from django.urls import path, include

urlpatterns = [
    # Demo API endpoints 
    path('demo/', include('apps.demo.urls')),
    
    # Authentication endpoints
    path('auth/', include('apps.authentication.urls')),
    
    # User management endpoints
    path('users/', include('apps.users.urls')),
]
