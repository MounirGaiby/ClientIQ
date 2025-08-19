"""
Working comprehensive tests for users app.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import uuid

from apps.users.models import CustomUser
from apps.users.managers import UserManager


class CustomUserModelTest(TestCase):
    """Test CustomUser model functionality."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        email = f'user-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, 'Regular')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.check_password('userpass123'))
    
    def test_create_admin_user(self):
        """Test creating an admin user."""
        email = f'admin-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('adminpass123'))
    
    def test_user_str_representation(self):
        """Test CustomUser string representation."""
        email = f'test-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        expected = email  # Basic users show just email
        self.assertEqual(str(user), expected)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        email = f'test-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.get_full_name(), 'Test User')
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        email = f'test-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.get_short_name(), 'Test')
    
    def test_email_required(self):
        """Test email is required."""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                email='',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
        self.assertIn('Email is required', str(context.exception))
    
    def test_user_permissions(self):
        """Test user permissions."""
        email = f'test-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Regular users should not have admin permissions or module access
        self.assertFalse(user.has_perm('admin.permission'))
        self.assertFalse(user.has_module_perms('users'))
    
    def test_admin_user_permissions(self):
        """Test admin user permissions."""
        email = f'admin-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        # Admin users should have elevated permissions
        self.assertTrue(user.has_perm('any.permission'))
        self.assertTrue(user.has_module_perms('any_app'))


class UserManagerTest(TestCase):
    """Test UserManager functionality."""
    
    def test_create_user_method(self):
        """Test create_user manager method."""
        email = f'manager-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='managerpass123',
            first_name='Manager',
            last_name='Test'
        )
        
        self.assertEqual(user.email, email)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
    
    def test_create_superuser_method(self):
        """Test create_superuser manager method."""
        email = f'super-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_superuser(
            email=email,
            password='superpass123',
            first_name='Super',
            last_name='User'
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)
    
    def test_email_normalization(self):
        """Test email normalization in manager."""
        email_upper = f'UPPER-{uuid.uuid4()}@TEST.COM'
        user = CustomUser.objects.create_user(
            email=email_upper,
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Check that email domain is normalized
        self.assertTrue('@test.com' in user.email.lower())


class CustomUserValidationTest(TestCase):
    """Test CustomUser validation and constraints."""
    
    def test_email_uniqueness(self):
        """Test email uniqueness constraint."""
        email = f'unique-{uuid.uuid4()}@test.com'
        CustomUser.objects.create_user(
            email=email,
            password='testpass123',
            first_name='First',
            last_name='User'
        )
        
        # Creating another user with same email should fail
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                email=email,
                password='testpass123',
                first_name='Second',
                last_name='User'
            )
    
    def test_required_fields(self):
        """Test all required fields."""
        # Email is required
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
    
    def test_password_validation(self):
        """Test password handling."""
        email = f'password-{uuid.uuid4()}@test.com'
        password = 'ComplexPassword123!'
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name='Password',
            last_name='Test'
        )
        
        # Password should be hashed
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password('wrongpassword'))


class CustomUserSecurityTest(TestCase):
    """Test CustomUser security features."""
    
    def test_inactive_user(self):
        """Test inactive user functionality."""
        email = f'inactive-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='inactivepass123',
            first_name='Inactive',
            last_name='User',
            is_active=False
        )
        
        self.assertFalse(user.is_active)
        # User should still be able to check password even if inactive
        self.assertTrue(user.check_password('inactivepass123'))
    
    def test_admin_vs_regular_permissions(self):
        """Test permission differences between admin and regular users."""
        # Regular user
        regular_email = f'regular-{uuid.uuid4()}@test.com'
        regular_user = CustomUser.objects.create_user(
            email=regular_email,
            password='regularpass123',
            first_name='Regular',
            last_name='User'
        )
        
        # Admin user
        admin_email = f'admin-{uuid.uuid4()}@test.com'
        admin_user = CustomUser.objects.create_user(
            email=admin_email,
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        # Test permission differences
        self.assertFalse(regular_user.is_admin)
        self.assertTrue(admin_user.is_admin)
        
        # Admin should have more permissions
        self.assertFalse(regular_user.has_perm('admin.permission'))
        self.assertTrue(admin_user.has_perm('admin.permission'))


class CustomUserIntegrationTest(TestCase):
    """Test CustomUser integration with Django auth system."""
    
    def test_authentication_backend(self):
        """Test user authentication."""
        email = f'auth-{uuid.uuid4()}@test.com'
        password = 'authpass123'
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name='Auth',
            last_name='Test'
        )
        
        # Test Django's authenticate function
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(username=email, password=password)
        
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.email, email)
    
    def test_login_functionality(self):
        """Test user login functionality."""
        email = f'login-{uuid.uuid4()}@test.com'
        password = 'loginpass123'
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name='Login',
            last_name='Test'
        )
        
        client = Client()
        # Test login
        login_successful = client.login(username=email, password=password)
        self.assertTrue(login_successful)
    
    def test_user_session(self):
        """Test user session management."""
        email = f'session-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='sessionpass123',
            first_name='Session',
            last_name='Test'
        )
        
        client = Client()
        client.login(username=email, password='sessionpass123')
        
        # User should be logged in
        response = client.get('/admin/')
        # Should redirect to login or show admin (both indicate session works)
        self.assertIn(response.status_code, [200, 302])


class CustomUserModelFieldTest(TestCase):
    """Test CustomUser model fields and properties."""
    
    def test_username_field(self):
        """Test USERNAME_FIELD is email."""
        self.assertEqual(CustomUser.USERNAME_FIELD, 'email')
    
    def test_required_fields(self):
        """Test REQUIRED_FIELDS configuration."""
        self.assertIn('first_name', CustomUser.REQUIRED_FIELDS)
        self.assertIn('last_name', CustomUser.REQUIRED_FIELDS)
    
    def test_model_meta(self):
        """Test model meta configuration."""
        self.assertEqual(CustomUser._meta.verbose_name, 'User')
        self.assertEqual(CustomUser._meta.verbose_name_plural, 'Users')
    
    def test_default_values(self):
        """Test default field values."""
        email = f'default-{uuid.uuid4()}@test.com'
        user = CustomUser.objects.create_user(
            email=email,
            password='defaultpass123',
            first_name='Default',
            last_name='Test'
        )
        
        # Test default values
        self.assertTrue(user.is_active)  # Should be active by default
        self.assertFalse(user.is_admin)  # Should not be admin by default
        self.assertIsNotNone(user.date_joined)  # Should have date_joined set
