"""
Custom authentication backends for tenant-aware authentication.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context


class TenantAuthenticationBackend(BaseBackend):
    """
    Custom authentication backend that authenticates users within tenant context.
    """
    
    def authenticate(self, request, username=None, password=None, tenant=None, **kwargs):
        """
        Authenticate user within tenant context.
        """
        if not username or not password or not tenant:
            return None
        
        try:
            with schema_context(tenant.schema_name):
                UserModel = get_user_model()
                user = UserModel.objects.get(email=username, is_active=True)
                
                if user.check_password(password):
                    return user
        except UserModel.DoesNotExist:
            # User doesn't exist in this tenant
            return None
        except Exception:
            # Any other error during authentication
            return None
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID within current tenant context.
        """
        try:
            UserModel = get_user_model()
            return UserModel.objects.get(pk=user_id, is_active=True)
        except UserModel.DoesNotExist:
            return None
