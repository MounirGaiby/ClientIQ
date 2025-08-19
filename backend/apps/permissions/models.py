from django.db import models


class Permission(models.Model):
    """
    Global permissions shared across all tenants.
    These define what actions are available in the system.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Permission name (e.g., 'can_view_reports')"
    )
    
    description = models.CharField(
        max_length=255,
        help_text="Human-readable description of the permission"
    )
    
    category = models.CharField(
        max_length=50,
        help_text="Category or module this permission belongs to"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this permission is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category}: {self.name}"


class Role(models.Model):
    """
    Global roles that can be assigned to users within tenants.
    These are templates that tenants can use.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Role name (e.g., 'Admin', 'Manager', 'User')"
    )
    
    description = models.CharField(
        max_length=255,
        help_text="Description of this role"
    )
    
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text="Permissions included in this role"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this role is assigned to new users by default"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']
    
    def __str__(self):
        return self.name
