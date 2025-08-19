"""
Working comprehensive tests for platform app.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib.admin.sites import AdminSite
import uuid

from apps.platform.models import SuperUser
from apps.platform.admin import SuperUserAdmin


class SuperUserModelTest(TestCase):
    """Test SuperUser model functionality."""
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        email = f'admin-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_superuser(
            email=email,
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(user.first_name, 'Admin')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_readonly)
        self.assertTrue(user.check_password('adminpass123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_readonly_user(self):
        """Test creating a readonly user."""
        email = f'readonly-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='readonlypass123',
            first_name='Read',
            last_name='Only',
            is_readonly=True
        )
        
        self.assertEqual(user.first_name, 'Read')
        self.assertTrue(user.is_readonly)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_superuser_str_representation(self):
        """Test SuperUser string representation."""
        email = f'test-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        expected = f"{email} (Platform Admin)"
        self.assertEqual(str(user), expected)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        email = f'test-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        email = f'test-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.get_short_name(), 'Test')
    
    def test_email_required(self):
        """Test email is required."""
        with self.assertRaises(ValueError) as context:
            SuperUser.objects.create_user(email='', password='testpass123')
        self.assertIn('Email is required', str(context.exception))
    
    def test_permissions_non_readonly(self):
        """Test permissions for non-readonly users."""
        email = f'test-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Non-readonly users should have all permissions
        self.assertTrue(user.has_perm('any.permission'))
        self.assertTrue(user.has_perms(['perm1', 'perm2']))
        self.assertTrue(user.has_module_perms('any_app'))
    
    def test_permissions_readonly(self):
        """Test permissions for readonly users."""
        user = SuperUser.objects.create_user(
            email='readonly@test.com',
            password='testpass123',
            is_readonly=True
        )
        
        # Readonly users should not have add/change/delete permissions
        self.assertFalse(user.has_perm('add_model'))
        self.assertFalse(user.has_perm('change_model'))
        self.assertFalse(user.has_perm('delete_model'))
        # But they can view
        self.assertTrue(user.has_perm('view_model'))


class SuperUserManagerTest(TestCase):
    """Test SuperUserManager functionality."""
    
    def test_create_user(self):
        """Test create_user method."""
        email = f'user-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        self.assertEqual(user.email, email)
        self.assertFalse(user.is_readonly)
        self.assertTrue(user.check_password('userpass123'))
    
    def test_create_superuser(self):
        """Test create_superuser method."""
        email = f'super-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_superuser(
            email=email,
            password='superpass123',
            first_name='Super',
            last_name='User'
        )
        
        self.assertEqual(user.email, email)
        self.assertFalse(user.is_readonly)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('superpass123'))


class SuperUserAdminTest(TestCase):
    """Test SuperUser admin functionality."""
    
    def setUp(self):
        """Set up admin test data."""
        self.admin_site = AdminSite()
        self.superuser_admin = SuperUserAdmin(SuperUser, self.admin_site)
    
    def test_admin_list_display(self):
        """Test admin list display configuration."""
        expected_fields = ['email', 'first_name', 'last_name', 'is_active', 'is_readonly', 'date_joined']
        self.assertEqual(list(self.superuser_admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test admin list filter configuration."""
        expected_filters = ['is_active', 'is_readonly', 'date_joined']
        self.assertEqual(list(self.superuser_admin.list_filter), expected_filters)
    
    def test_admin_search_fields(self):
        """Test admin search fields configuration."""
        expected_fields = ['email', 'first_name', 'last_name']
        self.assertEqual(list(self.superuser_admin.search_fields), expected_fields)
    
    def test_admin_readonly_fields(self):
        """Test admin readonly fields configuration."""
        expected_fields = ['date_joined', 'last_login']
        self.assertEqual(list(self.superuser_admin.readonly_fields), expected_fields)


class SuperUserViewTest(TestCase):
    """Test SuperUser view functionality."""
    
    def setUp(self):
        """Set up view test data."""
        self.client = Client()
        self.email = f'admin-{uuid.uuid4()}@platform.com'
        self.superuser = SuperUser.objects.create_superuser(
            email=self.email,
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
    
    def test_admin_login_redirect(self):
        """Test admin login redirect."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login
    
    def test_admin_login_success(self):
        """Test successful admin login."""
        login_successful = self.client.login(
            username=self.email,
            password='adminpass123'
        )
        self.assertTrue(login_successful)
    
    def test_admin_access_after_login(self):
        """Test admin access after login."""
        self.client.login(username=self.email, password='adminpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


class SuperUserSecurityTest(TestCase):
    """Test SuperUser security features."""
    
    def test_password_hashing(self):
        """Test password is properly hashed."""
        email = f'secure-{uuid.uuid4()}@platform.com'
        password = 'StrongPassword123!'
        user = SuperUser.objects.create_user(
            email=email,
            password=password,
            first_name='Secure',
            last_name='User'
        )
        
        # Password should be hashed
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_readonly_permissions(self):
        """Test readonly user security restrictions."""
        email = f'readonly-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='readonlypass123',
            first_name='Read',
            last_name='Only',
            is_readonly=True
        )
        
        # Readonly users should not have modify permissions
        self.assertFalse(user.has_perm('add'))
        self.assertFalse(user.has_perm('change'))
        self.assertFalse(user.has_perm('delete'))
    
    def test_active_user_functionality(self):
        """Test active/inactive user functionality."""
        email = f'inactive-{uuid.uuid4()}@platform.com'
        user = SuperUser.objects.create_user(
            email=email,
            password='inactivepass123',
            first_name='Inactive',
            last_name='User',
            is_active=False
        )
        
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password('inactivepass123'))
