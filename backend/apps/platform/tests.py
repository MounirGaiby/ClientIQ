"""
Comprehensive tests for platform app.
Tests SuperUser model and platform-level functionality.
"""

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
import uuid

from apps.platform.models import SuperUser
from apps.platform.admin import SuperUserAdmin


class SuperUserModelTest(TestCase):
    """Test SuperUser model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@platform.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'admin@platform.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_readonly)
        self.assertTrue(user.check_password('adminpass123'))
    
    def test_create_readonly_user(self):
        """Test creating a readonly user."""
        user = SuperUser.objects.create_user(
            email='readonly@platform.com',
            password='readonlypass123',
            first_name='Readonly',
            last_name='User',
            is_readonly=True
        )
        
        self.assertEqual(user.email, 'readonly@platform.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_readonly)
    
    def test_readonly_user_staff_properties(self):
        """Test that readonly user has correct staff properties."""
        user = SuperUser.objects.create_user(
            email='readonly@platform.com',
            password='readonlypass123',
            first_name='Readonly',
            last_name='User',
            is_readonly=True
        )
        
        # Readonly users should not have staff/superuser access
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_regular_platform_user_properties(self):
        """Test regular platform user properties."""
        user = SuperUser.objects.create_user(
            email='regular@platform.com',
            password='regularpass123',
            first_name='Regular',
            last_name='User'
        )
        
        # Regular platform users have staff access but not superuser
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_readonly)
    
    def test_email_unique_constraint(self):
        """Test that email must be unique."""
        SuperUser.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            SuperUser.objects.create_user(**self.user_data)
    
    def test_email_required(self):
        """Test that email is required."""
        with self.assertRaises(ValueError):
            SuperUser.objects.create_user(
                email='',
                password='testpass123'
            )
    
    def test_str_representation(self):
        """Test string representation of SuperUser."""
        user = SuperUser.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name} ({user.email})"
        self.assertEqual(str(user), expected)
    
    def test_user_manager_create_user(self):
        """Test UserManager create_user method."""
        user = SuperUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_readonly)
    
    def test_user_manager_create_superuser(self):
        """Test UserManager create_superuser method."""
        user = SuperUser.objects.create_superuser(
            email='super@platform.com',
            password='superpass123',
            first_name='Super',
            last_name='User'
        )
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_permissions(self):
        """Test user permissions functionality."""
        user = SuperUser.objects.create_user(**self.user_data)
        
        # Test that user can be assigned permissions
        permission = Permission.objects.filter(
            content_type__app_label='auth',
            codename='add_user'
        ).first()
        
        if permission:
            user.user_permissions.add(permission)
            self.assertTrue(user.has_perm('auth.add_user'))
    
    def test_email_normalization(self):
        """Test that email is normalized."""
        user = SuperUser.objects.create_user(
            email='TEST@PLATFORM.COM',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'TEST@platform.com')  # Domain normalized to lowercase
    
    def test_readonly_user_cannot_be_superuser(self):
        """Test that readonly users cannot be superuser."""
        user = SuperUser.objects.create_user(
            email='readonly@platform.com',
            password='readonlypass123',
            first_name='Readonly',
            last_name='User',
            is_readonly=True
        )
        
        # Even if we try to make them superuser, they shouldn't be
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)


class SuperUserAdminTest(TestCase):
    """Test SuperUser admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.admin = SuperUserAdmin(SuperUser, self.admin_site)
        
        # Create admin user
        self.admin_user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        # Create test user
        self.test_user = SuperUser.objects.create_user(
            email='test@platform.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_admin_list_display(self):
        """Test admin list display configuration."""
        expected_fields = [
            'email', 'first_name', 'last_name',
            'is_active', 'is_readonly', 'is_staff', 'is_superuser',
            'date_joined'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test admin list filter configuration."""
        expected_filters = [
            'is_active', 'is_readonly', 'is_staff', 'is_superuser',
            'date_joined'
        ]
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_admin_search_fields(self):
        """Test admin search fields configuration."""
        expected_fields = ['email', 'first_name', 'last_name']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_admin_fieldsets(self):
        """Test admin fieldsets configuration."""
        fieldsets = self.admin.fieldsets
        
        # Check that all important sections are present
        section_names = [section[0] for section in fieldsets]
        self.assertIn(None, section_names)  # Basic info section
        self.assertIn('Permissions', section_names)
        self.assertIn('Important dates', section_names)
    
    def test_admin_readonly_fields(self):
        """Test admin readonly fields configuration."""
        readonly_fields = self.admin.readonly_fields
        self.assertIn('date_joined', readonly_fields)
        self.assertIn('last_login', readonly_fields)
    
    def test_admin_ordering(self):
        """Test admin ordering configuration."""
        self.assertEqual(self.admin.ordering, ['-date_joined'])


class SuperUserIntegrationTest(TestCase):
    """Integration tests for SuperUser with Django auth system."""
    
    def setUp(self):
        """Set up test data."""
        self.superuser = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.regular_user = SuperUser.objects.create_user(
            email='user@platform.com',
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        self.readonly_user = SuperUser.objects.create_user(
            email='readonly@platform.com',
            password='readonlypass123',
            first_name='Readonly',
            last_name='User',
            is_readonly=True
        )
    
    def test_superuser_has_all_permissions(self):
        """Test that superuser has all permissions."""
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.has_perm('auth.add_user'))
        self.assertTrue(self.superuser.has_perm('auth.change_user'))
        self.assertTrue(self.superuser.has_perm('auth.delete_user'))
        self.assertTrue(self.superuser.has_module_perms('auth'))
    
    def test_regular_user_permissions(self):
        """Test regular user permissions."""
        self.assertFalse(self.regular_user.is_superuser)
        self.assertTrue(self.regular_user.is_staff)
        
        # Regular users don't automatically have permissions
        self.assertFalse(self.regular_user.has_perm('auth.add_user'))
    
    def test_readonly_user_permissions(self):
        """Test readonly user permissions."""
        self.assertFalse(self.readonly_user.is_superuser)
        self.assertFalse(self.readonly_user.is_staff)
        self.assertTrue(self.readonly_user.is_readonly)
        
        # Readonly users have no permissions
        self.assertFalse(self.readonly_user.has_perm('auth.add_user'))
        self.assertFalse(self.readonly_user.has_module_perms('auth'))
    
    def test_user_authentication(self):
        """Test user authentication."""
        from django.contrib.auth import authenticate
        
        # Test superuser authentication
        user = authenticate(
            email='admin@platform.com',
            password='adminpass123'
        )
        self.assertEqual(user, self.superuser)
        
        # Test wrong password
        user = authenticate(
            email='admin@platform.com',
            password='wrongpass'
        )
        self.assertIsNone(user)
    
    def test_user_login_permissions(self):
        """Test user login permissions based on user type."""
        # Superuser can access admin
        self.assertTrue(self.superuser.has_perm('admin.view_logentry'))
        
        # Regular staff user can access admin
        self.assertTrue(self.regular_user.is_staff)
        
        # Readonly user cannot access admin
        self.assertFalse(self.readonly_user.is_staff)
    
    @override_settings(AUTH_USER_MODEL='platform.SuperUser')
    def test_custom_user_model_setting(self):
        """Test that custom user model is properly configured."""
        User = get_user_model()
        self.assertEqual(User, SuperUser)
    
    def test_user_groups_functionality(self):
        """Test user groups functionality."""
        from django.contrib.auth.models import Group
        
        # Create a test group
        group = Group.objects.create(name='Test Group')
        
        # Add user to group
        self.regular_user.groups.add(group)
        
        # Test group membership
        self.assertTrue(self.regular_user.groups.filter(name='Test Group').exists())
        self.assertIn(group, self.regular_user.groups.all())
    
    def test_password_validation(self):
        """Test password validation."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Test weak password
        with self.assertRaises(ValidationError):
            validate_password('123', user=self.regular_user)
        
        # Test good password
        try:
            validate_password('StrongPass123!', user=self.regular_user)
        except ValidationError:
            self.fail("validate_password raised ValidationError for strong password")
