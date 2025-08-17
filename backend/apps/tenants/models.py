from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
import re


class Tenant(TenantMixin):
    """
    Tenant model for multi-tenant architecture.
    Each tenant gets its own database schema.
    """
    name = models.CharField(max_length=100, help_text="Company/Organization name")
    description = models.TextField(blank=True, help_text="Description of the tenant organization")
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Contact information
    contact_email = models.EmailField(blank=True, help_text="Primary contact email")
    contact_phone = models.CharField(max_length=20, blank=True, help_text="Primary contact phone")
    
    # Subscription information (will be linked to subscriptions app)
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
        ],
        default='trial'
    )
    
    def save(self, *args, **kwargs):
        """Override save to generate schema_name from name if not provided."""
        if not self.schema_name:
            # Generate schema name from tenant name
            # Convert to lowercase, replace spaces and special chars with underscores
            schema_name = re.sub(r'[^\w]', '_', self.name.lower())
            # Remove multiple consecutive underscores
            schema_name = re.sub(r'_+', '_', schema_name)
            # Remove leading/trailing underscores
            schema_name = schema_name.strip('_')
            # Ensure it starts with a letter
            if schema_name and not schema_name[0].isalpha():
                schema_name = f"tenant_{schema_name}"
            # Fallback if empty
            if not schema_name:
                schema_name = f"tenant_{self.pk or 'new'}"
            self.schema_name = schema_name
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"
    
    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """
    Domain model for tenant domains.
    Each tenant can have multiple domains.
    """
    pass
