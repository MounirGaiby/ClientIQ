from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class TenantUserManager(BaseUserManager):
    """Manager for tenant users (simplified)"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        For tenant users, 'superuser' just means admin within the tenant.
        No actual Django superuser powers - just tenant admin.
        """
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Clean tenant user model - NO superuser/staff fields.
    Only has is_admin flag for tenant-level permissions.
    Tenant users can NEVER access Django admin panel.
    """
    email = models.EmailField(
        unique=True,
        help_text="Email address used for authentication"
    )
    
    first_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="First name"
    )
    
    last_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Last name"
    )
    
    # Simple admin flag - if True, user has all permissions in their tenant
    is_admin = models.BooleanField(
        default=False,
        help_text="Tenant admin - has all permissions in this tenant"
    )
    
    # Basic user status
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active"
    )
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    
    # Contact info
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    
    # Profile info
    job_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title or position"
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or team"
    )
    
    # User preferences
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User-specific preferences and settings"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = TenantUserManager()
    
    # Explicitly prevent Django admin access
    @property
    def is_staff(self):
        """Tenant users are NEVER staff - only platform SuperUsers can access Django admin"""
        return False
    
    @property 
    def is_superuser(self):
        """Tenant users are NEVER superuser - only platform SuperUsers have superuser powers"""
        return False
    
    class Meta:
        verbose_name = "Tenant User"
        verbose_name_plural = "Tenant Users"
        ordering = ['email']
    
    def __str__(self):
        admin_status = " (Admin)" if self.is_admin else ""
        return f"{self.email}{admin_status}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        # Ensure email is lowercase
        self.email = self.email.lower()
        super().save(*args, **kwargs)
    
    def has_perm(self, perm, obj=None):
        """
        Permission check: admins have all permissions in their tenant
        """
        if not self.is_active:
            return False
        if self.is_admin:
            return True
        return super().has_perm(perm, obj)
    
    def has_perms(self, perm_list, obj=None):
        """
        Permission check: admins have all permissions in their tenant
        """
        if not self.is_active:
            return False
        if self.is_admin:
            return True
        return super().has_perms(perm_list, obj)
    
    def has_module_perms(self, app_label):
        """
        Permission check: admins have access to tenant modules only
        """
        if not self.is_active:
            return False
        if self.is_admin:
            # Allow access to tenant apps only, never Django admin apps
            tenant_apps = ['users', 'contacts', 'leads']
            return app_label in tenant_apps
        return False
