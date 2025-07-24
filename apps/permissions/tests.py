"""
Test suite for the Permissions app
Testing permission models, role groups, and permission management.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.test.client import Client

from apps.permissions.models import Permission, RoleGroup, RoleGroupPermission
from apps.common.services.permission_service import PermissionService


class PermissionModelTest(TestCase):
    """Test Permission model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.permission_data = {
            'name': 'Test Permission',
            'description': 'A test permission for unit testing',
            'is_super_user_only': False
        }
    
    def test_permission_creation(self):
        """Test creating a permission with valid data."""
        permission = Permission.objects.create(**self.permission_data)
        
        self.assertEqual(permission.name, 'Test Permission')
        self.assertEqual(permission.description, 'A test permission for unit testing')
        self.assertFalse(permission.is_super_user_only)
        self.assertTrue(permission.created_at)
    
    def test_permission_str_representation(self):
        """Test string representation of permission."""
        permission = Permission.objects.create(**self.permission_data)
        self.assertEqual(str(permission), 'Test Permission')
    
    def test_permission_unique_name(self):
        """Test that permission names must be unique."""
        Permission.objects.create(**self.permission_data)
        
        # Creating another permission with same name should fail
        with self.assertRaises(IntegrityError):
            Permission.objects.create(**self.permission_data)
    
    def test_super_user_permission(self):
        """Test creating a super user only permission."""
        super_permission = Permission.objects.create(
            name='Super User Permission',
            description='Only for super users',
            is_super_user_only=True
        )
        
        self.assertTrue(super_permission.is_super_user_only)
    
    def test_permission_name_validation(self):
        """Test permission name validation."""
        # Empty name should fail
        with self.assertRaises(ValidationError):
            permission = Permission(name='', description='Test')
            permission.full_clean()
        
        # Very long name should fail
        long_name = 'x' * 101  # Assuming max_length=100
        with self.assertRaises(ValidationError):
            permission = Permission(name=long_name, description='Test')
            permission.full_clean()


class RoleGroupModelTest(TestCase):
    """Test RoleGroup model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.role_group_data = {
            'name': 'Test Role Group',
            'description': 'A test role group for unit testing',
            'is_default': False
        }
    
    def test_role_group_creation(self):
        """Test creating a role group with valid data."""
        role_group = RoleGroup.objects.create(**self.role_group_data)
        
        self.assertEqual(role_group.name, 'Test Role Group')
        self.assertEqual(role_group.description, 'A test role group for unit testing')
        self.assertFalse(role_group.is_default)
        self.assertTrue(role_group.created_at)
    
    def test_role_group_str_representation(self):
        """Test string representation of role group."""
        role_group = RoleGroup.objects.create(**self.role_group_data)
        self.assertEqual(str(role_group), 'Test Role Group')
    
    def test_role_group_unique_name(self):
        """Test that role group names must be unique."""
        RoleGroup.objects.create(**self.role_group_data)
        
        # Creating another role group with same name should fail
        with self.assertRaises(IntegrityError):
            RoleGroup.objects.create(**self.role_group_data)
    
    def test_default_role_group(self):
        """Test creating a default role group."""
        default_role = RoleGroup.objects.create(
            name='Default Role',
            description='Default role for new users',
            is_default=True
        )
        
        self.assertTrue(default_role.is_default)
    
    def test_role_group_ordering(self):
        """Test role groups are ordered by name."""
        role_b = RoleGroup.objects.create(name='B Role')
        role_a = RoleGroup.objects.create(name='A Role')
        role_c = RoleGroup.objects.create(name='C Role')
        
        roles = list(RoleGroup.objects.all())
        self.assertEqual(roles[0], role_a)
        self.assertEqual(roles[1], role_b)
        self.assertEqual(roles[2], role_c)


class RoleGroupPermissionModelTest(TestCase):
    """Test RoleGroupPermission model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.permission = Permission.objects.create(
            name='Test Permission',
            description='Test permission'
        )
        self.role_group = RoleGroup.objects.create(
            name='Test Role Group',
            description='Test role group'
        )
    
    def test_role_group_permission_creation(self):
        """Test creating a role group permission relationship."""
        role_permission = RoleGroupPermission.objects.create(
            role_group=self.role_group,
            permission=self.permission
        )
        
        self.assertEqual(role_permission.role_group, self.role_group)
        self.assertEqual(role_permission.permission, self.permission)
        self.assertTrue(role_permission.created_at)
    
    def test_role_group_permission_str_representation(self):
        """Test string representation of role group permission."""
        role_permission = RoleGroupPermission.objects.create(
            role_group=self.role_group,
            permission=self.permission
        )
        expected_str = f"{self.role_group.name} - {self.permission.name}"
        self.assertEqual(str(role_permission), expected_str)
    
    def test_role_group_permission_unique_constraint(self):
        """Test that role group and permission combination must be unique."""
        RoleGroupPermission.objects.create(
            role_group=self.role_group,
            permission=self.permission
        )
        
        # Creating another relationship with same role and permission should fail
        with self.assertRaises(IntegrityError):
            RoleGroupPermission.objects.create(
                role_group=self.role_group,
                permission=self.permission
            )
    
    def test_multiple_permissions_per_role(self):
        """Test that a role group can have multiple permissions."""
        permission2 = Permission.objects.create(
            name='Second Permission',
            description='Second test permission'
        )
        
        RoleGroupPermission.objects.create(
            role_group=self.role_group,
            permission=self.permission
        )
        RoleGroupPermission.objects.create(
            role_group=self.role_group,
            permission=permission2
        )
        
        role_permissions = RoleGroupPermission.objects.filter(role_group=self.role_group)
        self.assertEqual(role_permissions.count(), 2)
    
    def test_multiple_roles_per_permission(self):
        """Test that a permission can be assigned to multiple role groups."""
        role_group2 = RoleGroup.objects.create(
            name='Second Role Group',
            description='Second test role group'
        )
        
        RoleGroupPermission.objects.create(
            role_group=self.role_group,
            permission=self.permission
        )
        RoleGroupPermission.objects.create(
            role_group=role_group2,
            permission=self.permission
        )
        
        permission_roles = RoleGroupPermission.objects.filter(permission=self.permission)
        self.assertEqual(permission_roles.count(), 2)


class PermissionServiceTest(TestCase):
    """Test PermissionService functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create some permissions
        self.view_permission = Permission.objects.create(
            name='View Data',
            description='Can view data'
        )
        self.edit_permission = Permission.objects.create(
            name='Edit Data',
            description='Can edit data'
        )
        self.delete_permission = Permission.objects.create(
            name='Delete Data',
            description='Can delete data'
        )
        self.super_permission = Permission.objects.create(
            name='Super Admin',
            description='Super admin access',
            is_super_user_only=True
        )
        
        # Create role groups
        self.admin_role = RoleGroup.objects.create(
            name='Admin',
            description='Administrator role'
        )
        self.user_role = RoleGroup.objects.create(
            name='User',
            description='Regular user role',
            is_default=True
        )
    
    def test_create_default_permissions(self):
        """Test creating default permissions."""
        # Clear existing permissions to test creation
        Permission.objects.all().delete()
        
        result = PermissionService.create_default_permissions()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['permissions_created'], 0)
        
        # Check that default permissions were created
        permissions = Permission.objects.all()
        self.assertGreater(permissions.count(), 0)
        
        # Check for specific expected permissions
        permission_names = [p.name for p in permissions]
        expected_permissions = [
            'View Dashboard', 'Manage Users', 'Manage Settings',
            'View Reports', 'Export Data', 'Manage Billing',
            'Delete Data', 'Super Admin Access'
        ]
        
        for expected_perm in expected_permissions:
            self.assertIn(expected_perm, permission_names)
    
    def test_create_default_role_groups(self):
        """Test creating default role groups."""
        # Clear existing role groups to test creation
        RoleGroup.objects.all().delete()
        
        result = PermissionService.create_default_role_groups()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['role_groups_created'], 0)
        
        # Check that default role groups were created
        role_groups = RoleGroup.objects.all()
        self.assertGreater(role_groups.count(), 0)
        
        # Check for specific expected role groups
        role_names = [r.name for r in role_groups]
        expected_roles = ['Admin', 'Manager', 'User']
        
        for expected_role in expected_roles:
            self.assertIn(expected_role, role_names)
        
        # Check that User role is marked as default
        user_role = RoleGroup.objects.get(name='User')
        self.assertTrue(user_role.is_default)
    
    def test_setup_default_permissions(self):
        """Test setting up default permission assignments."""
        # First create default permissions and role groups
        PermissionService.create_default_permissions()
        PermissionService.create_default_role_groups()
        
        result = PermissionService.setup_default_permissions()
        
        self.assertTrue(result['success'])
        self.assertGreater(result['assignments_created'], 0)
        
        # Check that role groups have permissions assigned
        admin_role = RoleGroup.objects.get(name='Admin')
        user_role = RoleGroup.objects.get(name='User')
        
        admin_permissions = RoleGroupPermission.objects.filter(role_group=admin_role)
        user_permissions = RoleGroupPermission.objects.filter(role_group=user_role)
        
        # Admin should have more permissions than User
        self.assertGreater(admin_permissions.count(), user_permissions.count())
        
        # User should have at least basic permissions
        self.assertGreater(user_permissions.count(), 0)
    
    def test_get_role_permissions(self):
        """Test getting permissions for a role group."""
        # Assign permissions to role
        RoleGroupPermission.objects.create(
            role_group=self.admin_role,
            permission=self.view_permission
        )
        RoleGroupPermission.objects.create(
            role_group=self.admin_role,
            permission=self.edit_permission
        )
        
        permissions = PermissionService.get_role_permissions(self.admin_role)
        
        self.assertEqual(len(permissions), 2)
        permission_names = [p['name'] for p in permissions]
        self.assertIn('View Data', permission_names)
        self.assertIn('Edit Data', permission_names)
    
    def test_get_all_permissions(self):
        """Test getting all permissions."""
        permissions = PermissionService.get_all_permissions()
        
        self.assertGreater(len(permissions), 0)
        
        # Check structure of returned permissions
        first_permission = permissions[0]
        self.assertIn('id', first_permission)
        self.assertIn('name', first_permission)
        self.assertIn('description', first_permission)
        self.assertIn('is_super_user_only', first_permission)
    
    def test_get_default_role_group(self):
        """Test getting the default role group."""
        default_role = PermissionService.get_default_role_group()
        
        self.assertEqual(default_role.name, 'User')
        self.assertTrue(default_role.is_default)


class PermissionAdminTest(TestCase):
    """Test Permission admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='testpass123'
        )
        self.client = Client()
    
    def test_admin_permission_list_view(self):
        """Test admin list view for permissions."""
        # Create test permissions
        Permission.objects.create(name='Admin Test Permission 1')
        Permission.objects.create(name='Admin Test Permission 2')
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Access admin list view
        response = self.client.get('/admin/permissions/permission/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test Permission 1')
        self.assertContains(response, 'Admin Test Permission 2')
    
    def test_admin_role_group_list_view(self):
        """Test admin list view for role groups."""
        # Create test role groups
        RoleGroup.objects.create(name='Admin Test Role 1')
        RoleGroup.objects.create(name='Admin Test Role 2')
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Access admin list view
        response = self.client.get('/admin/permissions/rolegroup/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test Role 1')
        self.assertContains(response, 'Admin Test Role 2')
    
    def test_admin_permission_creation(self):
        """Test creating a permission through admin."""
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Create permission via admin
        response = self.client.post('/admin/permissions/permission/add/', {
            'name': 'Admin Created Permission',
            'description': 'Permission created via admin',
            'is_super_user_only': False
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify permission was created
        permission = Permission.objects.get(name='Admin Created Permission')
        self.assertEqual(permission.description, 'Permission created via admin')


class PermissionIntegrationTest(TestCase):
    """Integration tests for permission functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create complete permission structure
        PermissionService.create_default_permissions()
        PermissionService.create_default_role_groups()
        PermissionService.setup_default_permissions()
    
    def test_complete_permission_setup(self):
        """Test complete permission system setup."""
        # Verify permissions exist
        permissions = Permission.objects.all()
        self.assertGreater(permissions.count(), 0)
        
        # Verify role groups exist
        role_groups = RoleGroup.objects.all()
        self.assertGreater(role_groups.count(), 0)
        
        # Verify assignments exist
        assignments = RoleGroupPermission.objects.all()
        self.assertGreater(assignments.count(), 0)
        
        # Verify specific role groups exist
        admin_role = RoleGroup.objects.filter(name='Admin').first()
        user_role = RoleGroup.objects.filter(name='User').first()
        
        self.assertIsNotNone(admin_role)
        self.assertIsNotNone(user_role)
        self.assertTrue(user_role.is_default)
        
        # Verify admin has more permissions than user
        admin_perms = RoleGroupPermission.objects.filter(role_group=admin_role).count()
        user_perms = RoleGroupPermission.objects.filter(role_group=user_role).count()
        
        self.assertGreater(admin_perms, user_perms)
    
    def test_permission_hierarchy(self):
        """Test permission hierarchy and inheritance."""
        admin_role = RoleGroup.objects.get(name='Admin')
        user_role = RoleGroup.objects.get(name='User')
        
        # Get permissions for each role
        admin_permissions = set(
            RoleGroupPermission.objects.filter(role_group=admin_role)
            .values_list('permission__name', flat=True)
        )
        user_permissions = set(
            RoleGroupPermission.objects.filter(role_group=user_role)
            .values_list('permission__name', flat=True)
        )
        
        # Admin should have all user permissions plus more
        self.assertTrue(user_permissions.issubset(admin_permissions))
        self.assertGreater(len(admin_permissions), len(user_permissions))
    
    def test_super_user_permissions(self):
        """Test super user only permissions."""
        super_permissions = Permission.objects.filter(is_super_user_only=True)
        
        if super_permissions.exists():
            # Super user permissions should not be assigned to regular roles
            regular_roles = RoleGroup.objects.exclude(name='Super Admin')
            
            for role in regular_roles:
                role_permissions = RoleGroupPermission.objects.filter(
                    role_group=role,
                    permission__in=super_permissions
                )
                self.assertEqual(role_permissions.count(), 0)
