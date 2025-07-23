"""
Authentication middleware for tenant-aware request processing.
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context


class TenantAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle tenant-specific authentication processing.
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
