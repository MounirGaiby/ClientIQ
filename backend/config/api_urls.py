"""
API URL configuration for ClientIQ.
"""
from django.urls import path, include

urlpatterns = [
    # Demo API endpoints 
    path('demo/', include('apps.demo.urls')),
    
    # Tenant validation endpoints (public)
    path('tenants/', include('apps.tenants.urls')),
    
    # Authentication endpoints
    path('auth/', include('apps.authentication.urls')),
    
    # User management endpoints
    path('users/', include('apps.users.urls')),
    
    # Contact management endpoints
    path('contacts/', include('apps.contacts.urls')),

    # Opportunities and pipeline endpoints
    path('opportunities/', include('apps.opportunities.urls')),
    
    # Activities and follow-up endpoints
    path('activities/', include('apps.activities.urls')),
]
