from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    User profile model that extends Django's built-in User model.
    """
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('user', 'Regular User'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
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
    
    # Tenant admin flag (for multi-tenant scenarios)
    is_tenant_admin = models.BooleanField(
        default=False,
        help_text="Whether this user is an admin for their tenant"
    )
    
    # User preferences
    preferences = models.JSONField(
        default=dict,
        help_text="User-specific preferences and settings"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.email} ({self.user_type})"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
