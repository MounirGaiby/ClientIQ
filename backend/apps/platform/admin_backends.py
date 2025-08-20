from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import SuperUser


class PlatformAdminBackend(BaseBackend):
    """
    Custom authentication backend for platform super users.
    Handles authentication for Django admin access.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            user = SuperUser.objects.get(email=username)
            if user.check_password(password) and user.is_active:
                return user
        except SuperUser.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        try:
            return SuperUser.objects.get(pk=user_id)
        except SuperUser.DoesNotExist:
            return None
    
    def has_perm(self, user_obj, perm, obj=None):
        """
        Check if user has permission.
        Readonly users can only view, full admins can do everything.
        """
        if not user_obj.is_active:
            return False
        
        if user_obj.is_readonly:
            # Readonly users can only view
            return 'view' in perm or perm.endswith('_view')
        
        # Full admin users have all permissions
        return True
    
    def has_module_perms(self, user_obj, app_label):
        """All active platform users can access all modules"""
        return user_obj.is_active
