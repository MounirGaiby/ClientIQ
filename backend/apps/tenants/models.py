from django_tenants.models import TenantMixin, DomainMixin
from django.db import models


class Tenant(TenantMixin):
    """
    Tenant model representing individual client organizations.
    Each tenant gets its own PostgreSQL schema.
    """
    # Company information
    name = models.CharField(
        max_length=100,
        help_text="Company or organization name"
    )
    
    # Contact information
    contact_email = models.EmailField(
        help_text="Primary contact email for this tenant"
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Primary contact phone number"
    )
    
    # Business information
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry or business sector"
    )
    
    company_size = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('500+', '500+ employees'),
        ],
        help_text="Size of the company"
    )
    
    # Subscription information
    PLAN_CHOICES = [
        ('trial', 'Trial'),
        ('basic', 'Basic'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='trial',
        help_text="Current subscription plan"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this tenant is active"
    )
    
    # Settings
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Tenant-specific settings and configurations"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: billing information
    billing_email = models.EmailField(
        blank=True,
        help_text="Email for billing notifications"
    )
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
    
    def __str__(self):
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    """
    Domain model for tenant-specific domains.
    Each tenant can have multiple domains pointing to their schema.
    """
    pass
