from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Custom user manager for email authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model that uses email as the unique identifier
    instead of username.
    """
    username = None  # Remove the username field
    email = models.EmailField(
        unique=True,
        help_text="Email address used for authentication"
    )
    
    # Additional fields
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
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
    
    # User type
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'), 
        ('user', 'Regular User'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='user',
        help_text="User type determines default permissions"
    )
    
    # Tenant admin flag (for multi-tenant scenarios)
    is_tenant_admin = models.BooleanField(
        default=False,
        help_text="Whether this user is an admin for their tenant"
    )
    
    # User preferences
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User-specific preferences and settings"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['email']
    
    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        # Ensure email is lowercase
        self.email = self.email.lower()
        super().save(*args, **kwargs)
