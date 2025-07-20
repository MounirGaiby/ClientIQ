"""
Permission Management Service

Service-Oriented Architecture (SOA) implementation for permission management.
Handles permission creation, role management, and tenant permission setup.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.permissions.models import Permission, RoleGroup, RoleGroupPermission
from apps.tenant_permissions.models import TenantRoleGroup, TenantRole, TenantUserRole

logger = logging.getLogger(__name__)


class PermissionService:
    """
    Service for managing permissions and roles across the multi-tenant system.
    
    This service follows SOA principles by encapsulating all permission
    management logic in a single, reusable service class.
    """
    
    @staticmethod
    def create_default_permissions():
        """
        Create default permissions in the public schema.
        These permissions are shared across all tenants.
        """
        default_permissions = [
            # User Management
            {
                'name': 'Create Users',
                'codename': 'can_create_users',
                'description': 'Create new users within the tenant',
                'category': 'User Management',
                'is_super_user_only': False,
            },
            {
                'name': 'Edit Users',
                'codename': 'can_edit_users',
                'description': 'Edit existing users within the tenant',
                'category': 'User Management',
                'is_super_user_only': False,
            },
            {
                'name': 'Delete Users',
                'codename': 'can_delete_users',
                'description': 'Delete users within the tenant',
                'category': 'User Management',
                'is_super_user_only': False,
            },
            {
                'name': 'View Users',
                'codename': 'can_view_users',
                'description': 'View user list and details within the tenant',
                'category': 'User Management',
                'is_super_user_only': False,
            },
            
            # Role Management
            {
                'name': 'Manage Roles',
                'codename': 'can_manage_roles',
                'description': 'Create, edit, and assign roles within the tenant',
                'category': 'Role Management',
                'is_super_user_only': False,
            },
            
            # Reports and Analytics
            {
                'name': 'View Reports',
                'codename': 'can_view_reports',
                'description': 'View reports and analytics',
                'category': 'Reports',
                'is_super_user_only': False,
            },
            {
                'name': 'Export Data',
                'codename': 'can_export_data',
                'description': 'Export data and reports',
                'category': 'Reports',
                'is_super_user_only': False,
            },
            
            # Settings
            {
                'name': 'Manage Settings',
                'codename': 'can_manage_settings',
                'description': 'Manage tenant settings and configuration',
                'category': 'Settings',
                'is_super_user_only': False,
            },
            
            # Super User Only Permissions
            {
                'name': 'Delete Tenant',
                'codename': 'can_delete_tenant',
                'description': 'Delete entire tenant and all associated data',
                'category': 'System',
                'is_super_user_only': True,
            },
            {
                'name': 'Manage Subscriptions',
                'codename': 'can_manage_subscriptions',
                'description': 'Manage tenant subscriptions and billing',
                'category': 'System',
                'is_super_user_only': True,
            },
        ]
        
        created_permissions = []
        for perm_data in default_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults=perm_data
            )
            if created:
                created_permissions.append(permission)
                logger.info(f"Created permission: {permission.name}")
        
        return created_permissions
    
    @staticmethod
    def create_default_role_groups():
        """
        Create default role groups in the public schema.
        """
        # Create Admin role group with all tenant-level permissions
        admin_role_group, created = RoleGroup.objects.get_or_create(
            name='Admin',
            defaults={
                'description': 'Full administrative access to tenant',
                'is_default': True,
                'is_super_user_group': False,
                'is_active': True,
            }
        )
        
        if created:
            # Add all non-super-user permissions to admin role group
            tenant_permissions = Permission.objects.filter(is_super_user_only=False)
            for permission in tenant_permissions:
                RoleGroupPermission.objects.get_or_create(
                    role_group=admin_role_group,
                    permission=permission
                )
            logger.info(f"Created Admin role group with {tenant_permissions.count()} permissions")
        
        # Create Manager role group with limited permissions
        manager_role_group, created = RoleGroup.objects.get_or_create(
            name='Manager',
            defaults={
                'description': 'Management access with user and report permissions',
                'is_default': True,
                'is_super_user_group': False,
                'is_active': True,
            }
        )
        
        if created:
            # Add specific permissions for managers
            manager_permission_codes = [
                'can_view_users',
                'can_edit_users',
                'can_create_users',
                'can_view_reports',
                'can_export_data',
            ]
            manager_permissions = Permission.objects.filter(
                codename__in=manager_permission_codes
            )
            for permission in manager_permissions:
                RoleGroupPermission.objects.get_or_create(
                    role_group=manager_role_group,
                    permission=permission
                )
            logger.info(f"Created Manager role group with {manager_permissions.count()} permissions")
        
        # Create User role group with basic permissions
        user_role_group, created = RoleGroup.objects.get_or_create(
            name='User',
            defaults={
                'description': 'Basic user access with view permissions',
                'is_default': True,
                'is_super_user_group': False,
                'is_active': True,
            }
        )
        
        if created:
            # Add basic permissions for users
            user_permission_codes = [
                'can_view_users',
                'can_view_reports',
            ]
            user_permissions = Permission.objects.filter(
                codename__in=user_permission_codes
            )
            for permission in user_permissions:
                RoleGroupPermission.objects.get_or_create(
                    role_group=user_role_group,
                    permission=permission
                )
            logger.info(f"Created User role group with {user_permissions.count()} permissions")
        
        return [admin_role_group, manager_role_group, user_role_group]
    
    @classmethod
    @transaction.atomic
    def setup_tenant_permissions(cls, tenant):
        """
        Set up permissions for a new tenant by duplicating default role groups.
        
        Args:
            tenant: Tenant instance
        """
        logger.info(f"Setting up permissions for tenant: {tenant.name}")
        
        # Switch to tenant schema
        from django_tenants.utils import schema_context
        
        with schema_context(tenant.schema_name):
            # Get default role groups from public schema
            default_role_groups = RoleGroup.objects.using('default').filter(
                is_default=True,
                is_active=True
            ).prefetch_related('role_permissions__permission')
            
            created_role_groups = []
            
            for role_group in default_role_groups:
                # Create tenant role group
                tenant_role_group, created = TenantRoleGroup.objects.get_or_create(
                    name=role_group.name,
                    defaults={
                        'description': role_group.description,
                        'original_role_group_id': role_group.id,
                        'is_active': True,
                    }
                )
                
                if created:
                    # Get permission codenames for this role group
                    permission_codenames = [
                        rp.permission.codename 
                        for rp in role_group.role_permissions.all()
                    ]
                    tenant_role_group.permission_codenames = permission_codenames
                    tenant_role_group.save()
                    
                    # Create default role within the role group
                    TenantRole.objects.get_or_create(
                        name=role_group.name,
                        role_group=tenant_role_group,
                        defaults={
                            'description': f"Default {role_group.name} role",
                            'is_active': True,
                        }
                    )
                    
                    created_role_groups.append(tenant_role_group)
                    logger.info(
                        f"Created tenant role group: {tenant_role_group.name} "
                        f"with {len(permission_codenames)} permissions"
                    )
            
            return created_role_groups
    
    @classmethod
    def assign_admin_role(cls, user, tenant):
        """
        Assign admin role to a user within a tenant.
        
        Args:
            user: TenantUser instance
            tenant: Tenant instance
        """
        from django_tenants.utils import schema_context
        
        with schema_context(tenant.schema_name):
            try:
                # Get admin role group
                admin_role_group = TenantRoleGroup.objects.get(name='Admin')
                admin_role = TenantRole.objects.get(
                    name='Admin',
                    role_group=admin_role_group
                )
                
                # Assign role to user
                user_role, created = TenantUserRole.objects.get_or_create(
                    user=user,
                    role=admin_role,
                    defaults={
                        'is_active': True,
                    }
                )
                
                if created:
                    logger.info(f"Assigned admin role to user: {user.email}")
                    return user_role
                else:
                    logger.info(f"User {user.email} already has admin role")
                    return user_role
                    
            except (TenantRoleGroup.DoesNotExist, TenantRole.DoesNotExist) as e:
                logger.error(f"Admin role not found for tenant {tenant.name}: {e}")
                raise
    
    @staticmethod
    def get_permission_summary() -> Dict[str, Any]:
        """
        Get a summary of all permissions and role groups.
        
        Returns:
            Dictionary with permission and role group statistics
        """
        return {
            'total_permissions': Permission.objects.count(),
            'tenant_permissions': Permission.objects.filter(is_super_user_only=False).count(),
            'super_user_permissions': Permission.objects.filter(is_super_user_only=True).count(),
            'total_role_groups': RoleGroup.objects.count(),
            'default_role_groups': RoleGroup.objects.filter(is_default=True).count(),
            'permission_categories': list(
                Permission.objects.values_list('category', flat=True).distinct()
            ),
        }
