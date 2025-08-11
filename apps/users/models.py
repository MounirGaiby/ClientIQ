from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator


class TenantUser(AbstractUser):
    """
    Tenant-specific user model.
    Each tenant has its own isolated set of users.
    """
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('user', 'Regular User'),
    ]
    
    # Override email to be required and unique within tenant
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address (must be unique within tenant)"
    )
    
    # Additional user fields
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user',
        help_text="User type determines default permissions"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    
    # User preferences
    preferences = models.JSONField(
        default=dict,
        help_text="User-specific preferences and settings"
    )
    
    # Profile information
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or team"
    )
    
    job_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title or position"
    )
    
    # Account status
    is_tenant_admin = models.BooleanField(
        default=False,
        help_text="Whether this user is a tenant administrator"
    )
    
    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Remove username field and fix reverse accessor conflicts
    username = None
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='tenant_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='tenant_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    class Meta:
        verbose_name = "Tenant User"
        verbose_name_plural = "Tenant Users"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_permissions(self):
        """
        Get all permissions for this user based on their roles.
        Returns a list of permission codenames.
        """
        from apps.tenant_permissions.models import TenantUserRole
        
        permission_codenames = set()
        
        # Get all active roles for this user
        user_roles = TenantUserRole.objects.filter(
            user=self,
            is_active=True,
            role__is_active=True,
            role__role_group__is_active=True
        ).select_related('role__role_group')
        
        # Collect all permission codenames from role groups
        for user_role in user_roles:
            permission_codenames.update(
                user_role.role.role_group.permission_codenames
            )
        
        return list(permission_codenames)
    
    def has_permission(self, permission_codename):
        """
        Check if user has a specific permission.
        """
        return permission_codename in self.get_permissions()


# Add custom manager after class definition to avoid circular imports
from .managers import UserManager
TenantUser.add_to_class('objects', UserManager())
