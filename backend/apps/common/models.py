from django.db import models
from django.contrib.auth import get_user_model


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all tenant models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class TenantAwareModel(BaseModel):
    """
    Abstract model that automatically tracks the user who created/modified records.
    This is useful for tenant-specific audit trails.
    """
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True
