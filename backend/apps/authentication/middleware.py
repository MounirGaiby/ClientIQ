"""
Authentication middleware for tenant-aware request processing.
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model, logout
from django_tenants.utils import schema_context
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


class TenantOnlyAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to block authentication on public schema and enforce tenant-only login.
    Users can only login to tenant domains, not the base domain.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        """
        Process request with tenant context.
        """
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        """
        Block authentication attempts on public schema.
        """
        # Check if we're on the public schema (base domain)
        if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
            # If user is trying to authenticate on public schema, block it
            if request.path.startswith('/api/auth/') or request.path.startswith('/admin/'):
                if request.method == 'POST':
                    return JsonResponse({
                        'error': 'Authentication not allowed on base domain. Please use your tenant domain.'
                    }, status=403)
            
            # If user is somehow authenticated on public schema, log them out
            if request.user.is_authenticated:
                logout(request)
        
        # For tenant schemas, ensure user exists in current tenant
        elif hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
            if request.user.is_authenticated:
                try:
                    with schema_context(request.tenant.schema_name):
                        UserModel = get_user_model()
                        UserModel.objects.get(pk=request.user.pk, is_active=True)
                except UserModel.DoesNotExist:
                    # User doesn't exist in this tenant, log them out
                    logout(request)
        
        return None
    
    def process_response(self, request, response):
        """
        Process response after view processing.
        """
        return response


class TenantAuthenticationMiddleware(MiddlewareMixin):
    """
    Legacy middleware - kept for backward compatibility.
    Use TenantOnlyAuthenticationMiddleware instead.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        """
        Process request with tenant context.
        """
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        """
        Process request to inject tenant context for authentication.
        """
        # Tenant context should already be set by django-tenants middleware
        if hasattr(request, 'tenant') and request.user.is_authenticated:
            # Ensure user exists in current tenant context
            try:
                with schema_context(request.tenant.schema_name):
                    UserModel = get_user_model()
                    UserModel.objects.get(pk=request.user.pk, is_active=True)
            except UserModel.DoesNotExist:
                # User doesn't exist in this tenant, log them out
                from django.contrib.auth import logout
                logout(request)
        
        return None
    
    def process_response(self, request, response):
        """
        Process response after view processing.
        """
        return response
