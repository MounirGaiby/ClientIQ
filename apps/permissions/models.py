from django.db import models
from django.contrib.auth.models import Permission as DjangoPermission


class Permission(models.Model):
    """
    Custom permission model for the multi-tenant system.
    These permissions are stored in the public schema and shared across all tenants.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Human-readable name of the permission"
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique code name for the permission (e.g., 'can_create_users')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this permission allows"
    )
    category = models.CharField(
        max_length=50,
        help_text="Permission category (e.g., 'User Management', 'Reports')"
    )
    is_super_user_only = models.BooleanField(
        default=False,
        help_text="True if this permission is only for super users (app owners/devs)"
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


class RoleGroup(models.Model):
    """
    Role groups define collections of permissions.
    These are stored in public schema and can be duplicated to tenant schemas.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the role group (e.g., 'Admin', 'Manager')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the role group"
    )
    permissions = models.ManyToManyField(
        Permission,
        through='RoleGroupPermission',
        help_text="Permissions assigned to this role group"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this role group should be created by default in new tenants"
    )
    is_super_user_group = models.BooleanField(
        default=False,
        help_text="True if this role group is for super users only"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role group is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Role Group"
        verbose_name_plural = "Role Groups"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RoleGroupPermission(models.Model):
    """
    Through model for RoleGroup and Permission many-to-many relationship.
    Allows for additional metadata on the relationship.
    """
    role_group = models.ForeignKey(
        RoleGroup,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='group_permissions'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['role_group', 'permission']
        verbose_name = "Role Group Permission"
        verbose_name_plural = "Role Group Permissions"
    
    def __str__(self):
        return f"{self.role_group.name} -> {self.permission.name}"
