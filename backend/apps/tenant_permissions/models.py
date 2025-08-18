from django.db import models
from django.contrib.auth import get_user_model


class TenantRoleGroup(models.Model):
    """
    Tenant-specific role groups.
    These are duplicated from the public schema's RoleGroup model for each tenant.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the role group"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the role group"
    )
    # Store permission codenames as JSON since we can't directly reference public schema
    permission_codenames = models.JSONField(
        default=list,
        help_text="List of permission codenames assigned to this role group"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role group is currently active"
    )
    # Reference to the original role group in public schema
    original_role_group_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of the original role group in public schema"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tenant Role Group"
        verbose_name_plural = "Tenant Role Groups"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TenantRole(models.Model):
    """
    Individual roles within a tenant.
    Users can have multiple roles within their tenant.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the role"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the role"
    )
    role_group = models.ForeignKey(
        TenantRoleGroup,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text="Role group this role belongs to"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tenant Role"
        verbose_name_plural = "Tenant Roles"
        ordering = ['role_group__name', 'name']
        unique_together = ['name', 'role_group']
    
    def __str__(self):
        return f"{self.role_group.name} - {self.name}"


class TenantUserRole(models.Model):
    """
    Association between users and their roles within a tenant.
    """
    user = models.ForeignKey(
        'users.TenantUser',  # Forward reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='user_roles',
        null=True,  # Allow null temporarily for migration
        blank=True
    )
    role = models.ForeignKey(
        TenantRole,
        on_delete=models.CASCADE,
        related_name='user_assignments',
        null=True,  # Allow null temporarily for migration
        blank=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'users.TenantUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        help_text="User who assigned this role"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role assignment is currently active"
    )
    
    class Meta:
        verbose_name = "Tenant User Role"
        verbose_name_plural = "Tenant User Roles"
        unique_together = ['user', 'role']
    
    def __str__(self):
        return f"{self.user} -> {self.role}"
