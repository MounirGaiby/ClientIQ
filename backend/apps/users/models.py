from django.contrib.auth.models import AbstractUser, BaseUserManager
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
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Simplified tenant user model.
    No superuser/staff complexity - just regular users with optional admin flag.
    """
    username = None  # Remove username field
    email = models.EmailField(
        unique=True,
        help_text="Email address used for authentication"
    )
    
    # Simple admin flag - if True, user has all permissions in their tenant
    is_admin = models.BooleanField(
        default=False,
        help_text="Tenant admin - has all permissions in this tenant"
    )
    
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
        if self.is_admin:
            return True
        return super().has_perm(perm, obj)
    
    def has_perms(self, perm_list, obj=None):
        """
        Permission check: admins have all permissions in their tenant
        """
        if self.is_admin:
            return True
        return super().has_perms(perm_list, obj)
    
    def has_module_perms(self, app_label):
        """
        Permission check: admins have module access in their tenant
        """
        if self.is_admin:
            return True
        return super().has_module_perms(app_label)
