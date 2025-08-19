"""
Comprehensive tests for users app.
Tests CustomUser model, managers, and user functionality within tenant context.
"""

from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.sites import AdminSite
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import tenant_context

from apps.users.models import CustomUser
from apps.users.managers import CustomUserManager
from apps.tenants.models import Tenant, Domain


User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test CustomUser model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@testcorp.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'department': 'Engineering',
            'job_title': 'Software Developer'
        }
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@testcorp.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.department, 'Engineering')
        self.assertEqual(user.job_title, 'Software Developer')
        self.assertEqual(user.user_type, 'user')  # Default user type
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_admin_user(self):
        """Test creating an admin user."""
        user_data = self.user_data.copy()
        user_data['is_admin'] = True
        user_data['user_type'] = 'admin'
        
        user = User.objects.create_user(**user_data)
        
        self.assertTrue(user.is_admin)
        self.assertEqual(user.user_type, 'admin')
        # is_staff and is_superuser are computed properties
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_manager_user(self):
        """Test creating a manager user."""
        user_data = self.user_data.copy()
        user_data['user_type'] = 'manager'
        
        user = User.objects.create_user(**user_data)
        
        self.assertEqual(user.user_type, 'manager')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_email_unique_constraint(self):
        """Test that email must be unique within tenant."""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)
    
    def test_email_required(self):
        """Test that email is required."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123'
            )
    
    def test_str_representation(self):
        """Test string representation of CustomUser."""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name} ({user.email})"
        self.assertEqual(str(user), expected)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.first_name} {user.last_name}"
        self.assertEqual(user.get_full_name(), expected)
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), user.first_name)
    
    def test_user_type_choices(self):
        """Test user type choices."""
        user_types = ['admin', 'manager', 'user']
        
        for user_type in user_types:
            user_data = self.user_data.copy()
            user_data['email'] = f'{user_type}@testcorp.com'
            user_data['user_type'] = user_type
            
            user = User.objects.create_user(**user_data)
            self.assertEqual(user.user_type, user_type)
    
    def test_phone_number_optional(self):
        """Test that phone number is optional."""
        user_data = self.user_data.copy()
        user_data['phone_number'] = '+1234567890'
        
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.phone_number, '+1234567890')
        
        # Test without phone number
        user_data['email'] = 'test2@testcorp.com'
        user_data.pop('phone_number', None)
        
        user2 = User.objects.create_user(**user_data)
        self.assertEqual(user2.phone_number, '')
    
    def test_email_normalization(self):
        """Test that email is normalized."""
        user_data = self.user_data.copy()
        user_data['email'] = 'TEST@TESTCORP.COM'
        
        user = User.objects.create_user(**user_data)
        self.assertEqual(user.email, 'TEST@testcorp.com')  # Domain normalized
    
    def test_admin_user_permissions(self):
        """Test that admin users have special permissions."""
        admin_user = User.objects.create_user(
            email='admin@testcorp.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        # Admin users should be staff and superuser
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        
        # Admin users should have all permissions
        self.assertTrue(admin_user.has_perm('auth.add_user'))
        self.assertTrue(admin_user.has_perm('auth.change_user'))
        self.assertTrue(admin_user.has_module_perms('auth'))


class CustomUserManagerTest(TestCase):
    """Test CustomUserManager functionality."""
    
    def test_create_user_method(self):
        """Test create_user method."""
        user = User.objects.create_user(
            email='test@testcorp.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'test@testcorp.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
    
    def test_create_user_without_email(self):
        """Test create_user method without email raises error."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email='',
                password='testpass123'
            )
        
        self.assertIn('email', str(context.exception).lower())
    
    def test_create_superuser_method(self):
        """Test create_superuser method."""
        user = User.objects.create_superuser(
            email='admin@testcorp.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(user.email, 'admin@testcorp.com')
        self.assertTrue(user.check_password('adminpass123'))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_superuser_validates_admin_flag(self):
        """Test that create_superuser validates is_admin=True."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@testcorp.com',
                password='adminpass123',
                is_admin=False
            )


class CustomUserAuthenticationTest(TestCase):
    """Test user authentication functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@testcorp.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@testcorp.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
    
    def test_user_authentication(self):
        """Test user authentication with email and password."""
        user = authenticate(
            email='test@testcorp.com',
            password='testpass123'
        )
        self.assertEqual(user, self.user)
    
    def test_authentication_with_wrong_password(self):
        """Test authentication fails with wrong password."""
        user = authenticate(
            email='test@testcorp.com',
            password='wrongpass'
        )
        self.assertIsNone(user)
    
    def test_authentication_with_wrong_email(self):
        """Test authentication fails with wrong email."""
        user = authenticate(
            email='wrong@testcorp.com',
            password='testpass123'
        )
        self.assertIsNone(user)
    
    def test_inactive_user_authentication(self):
        """Test that inactive users cannot authenticate."""
        self.user.is_active = False
        self.user.save()
        
        user = authenticate(
            email='test@testcorp.com',
            password='testpass123'
        )
        self.assertIsNone(user)
    
    def test_admin_user_authentication(self):
        """Test admin user authentication."""
        user = authenticate(
            email='admin@testcorp.com',
            password='adminpass123'
        )
        self.assertEqual(user, self.admin_user)
        self.assertTrue(user.is_admin)


class CustomUserPermissionTest(TestCase):
    """Test user permission functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.regular_user = User.objects.create_user(
            email='user@testcorp.com',
            password='userpass123',
            first_name='Regular',
            last_name='User'
        )
        
        self.admin_user = User.objects.create_user(
            email='admin@testcorp.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        
        self.manager_user = User.objects.create_user(
            email='manager@testcorp.com',
            password='managerpass123',
            first_name='Manager',
            last_name='User',
            user_type='manager'
        )
    
    def test_admin_user_has_all_permissions(self):
        """Test that admin users have all permissions."""
        # Admin users should have superuser permissions
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.has_perm('auth.add_user'))
        self.assertTrue(self.admin_user.has_perm('auth.change_user'))
        self.assertTrue(self.admin_user.has_perm('auth.delete_user'))
        self.assertTrue(self.admin_user.has_module_perms('auth'))
        self.assertTrue(self.admin_user.has_module_perms('users'))
    
    def test_regular_user_permissions(self):
        """Test regular user permissions."""
        # Regular users should not have superuser permissions
        self.assertFalse(self.regular_user.is_superuser)
        self.assertFalse(self.regular_user.has_perm('auth.add_user'))
        self.assertFalse(self.regular_user.has_perm('auth.change_user'))
        self.assertFalse(self.regular_user.has_perm('auth.delete_user'))
        self.assertFalse(self.regular_user.has_module_perms('auth'))
    
    def test_user_groups(self):
        """Test user groups functionality."""
        # Create a group
        group = Group.objects.create(name='Test Group')
        
        # Add user to group
        self.regular_user.groups.add(group)
        
        # Test group membership
        self.assertTrue(self.regular_user.groups.filter(name='Test Group').exists())
        self.assertIn(group, self.regular_user.groups.all())
    
    def test_user_specific_permissions(self):
        """Test assigning specific permissions to users."""
        # Get a permission
        permission = Permission.objects.filter(
            content_type__app_label='auth',
            codename='view_user'
        ).first()
        
        if permission:
            # Assign permission to regular user
            self.regular_user.user_permissions.add(permission)
            
            # Test permission
            self.assertTrue(self.regular_user.has_perm('auth.view_user'))
            
            # Test that user doesn't have other permissions
            self.assertFalse(self.regular_user.has_perm('auth.add_user'))


class CustomUserValidationTest(TestCase):
    """Test user validation functionality."""
    
    def test_email_validation(self):
        """Test email validation."""
        # Test invalid email
        with self.assertRaises(ValidationError):
            user = User(
                email='invalid-email',
                first_name='Test',
                last_name='User'
            )
            user.full_clean()
    
    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        # Test missing email
        with self.assertRaises(ValidationError):
            user = User(
                first_name='Test',
                last_name='User'
            )
            user.full_clean()
    
    def test_user_type_validation(self):
        """Test user type validation."""
        # Test valid user types
        valid_types = ['admin', 'manager', 'user']
        for user_type in valid_types:
            user = User(
                email=f'{user_type}@testcorp.com',
                first_name='Test',
                last_name='User',
                user_type=user_type
            )
            try:
                user.full_clean()
            except ValidationError:
                self.fail(f"Valid user type '{user_type}' failed validation")
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Test valid phone numbers
        valid_phones = [
            '+1234567890',
            '(555) 123-4567',
            '555-123-4567',
            '555.123.4567',
            ''  # Empty is valid
        ]
        
        for phone in valid_phones:
            user = User(
                email=f'test{phone.replace("+", "").replace("(", "").replace(")", "").replace("-", "").replace(".", "").replace(" ", "")}@testcorp.com',
                first_name='Test',
                last_name='User',
                phone_number=phone
            )
            try:
                user.full_clean()
            except ValidationError:
                self.fail(f"Valid phone number '{phone}' failed validation")


class CustomUserQueryTest(TestCase):
    """Test user query functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create users with different types
        self.admin_user = User.objects.create_user(
            email='admin@testcorp.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_admin=True,
            user_type='admin'
        )
        
        self.manager_user = User.objects.create_user(
            email='manager@testcorp.com',
            password='managerpass123',
            first_name='Manager',
            last_name='User',
            user_type='manager'
        )
        
        self.regular_user = User.objects.create_user(
            email='user@testcorp.com',
            password='userpass123',
            first_name='Regular',
            last_name='User',
            user_type='user'
        )
    
    def test_filter_by_user_type(self):
        """Test filtering users by type."""
        admins = User.objects.filter(user_type='admin')
        managers = User.objects.filter(user_type='manager')
        users = User.objects.filter(user_type='user')
        
        self.assertIn(self.admin_user, admins)
        self.assertIn(self.manager_user, managers)
        self.assertIn(self.regular_user, users)
        
        self.assertEqual(admins.count(), 1)
        self.assertEqual(managers.count(), 1)
        self.assertEqual(users.count(), 1)
    
    def test_filter_by_admin_status(self):
        """Test filtering users by admin status."""
        admin_users = User.objects.filter(is_admin=True)
        non_admin_users = User.objects.filter(is_admin=False)
        
        self.assertIn(self.admin_user, admin_users)
        self.assertIn(self.manager_user, non_admin_users)
        self.assertIn(self.regular_user, non_admin_users)
        
        self.assertEqual(admin_users.count(), 1)
        self.assertEqual(non_admin_users.count(), 2)
    
    def test_search_by_email(self):
        """Test searching users by email."""
        user = User.objects.filter(email='admin@testcorp.com').first()
        self.assertEqual(user, self.admin_user)
    
    def test_search_by_name(self):
        """Test searching users by name."""
        users = User.objects.filter(first_name__icontains='admin')
        self.assertIn(self.admin_user, users)
        
        users = User.objects.filter(last_name__icontains='user')
        self.assertEqual(users.count(), 3)  # All users have 'User' as last name
    
    def test_ordering(self):
        """Test user ordering."""
        # Test default ordering (by date_joined)
        users = list(User.objects.all())
        dates = [user.date_joined for user in users]
        self.assertEqual(dates, sorted(dates))
        
        # Test ordering by name
        users_by_name = list(User.objects.order_by('first_name'))
        names = [user.first_name for user in users_by_name]
        self.assertEqual(names, sorted(names))


class CustomUserIntegrationTest(TestCase):
    """Integration tests for CustomUser with other components."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@testcorp.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_with_groups_and_permissions(self):
        """Test user functionality with groups and permissions."""
        # Create group and permission
        group = Group.objects.create(name='Test Group')
        permission = Permission.objects.filter(
            content_type__app_label='auth',
            codename='view_user'
        ).first()
        
        if permission:
            # Add permission to group
            group.permissions.add(permission)
            
            # Add user to group
            self.user.groups.add(group)
            
            # Test that user has permission through group
            self.assertTrue(self.user.has_perm('auth.view_user'))
    
    def test_password_change(self):
        """Test password change functionality."""
        original_password = 'testpass123'
        new_password = 'newtestpass456'
        
        # Verify original password works
        self.assertTrue(self.user.check_password(original_password))
        
        # Change password
        self.user.set_password(new_password)
        self.user.save()
        
        # Verify new password works and old doesn't
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(self.user.check_password(original_password))
    
    def test_user_deactivation(self):
        """Test user deactivation."""
        self.assertTrue(self.user.is_active)
        
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        # Test that user is deactivated
        self.assertFalse(self.user.is_active)
        
        # Test that authentication fails for inactive user
        user = authenticate(
            email='test@testcorp.com',
            password='testpass123'
        )
        self.assertIsNone(user)
    
    def test_user_data_update(self):
        """Test updating user data."""
        original_name = self.user.first_name
        new_name = 'Updated'
        
        # Update user data
        self.user.first_name = new_name
        self.user.department = 'Marketing'
        self.user.job_title = 'Marketing Manager'
        self.user.save()
        
        # Refresh from database
        self.user.refresh_from_db()
        
        # Verify updates
        self.assertEqual(self.user.first_name, new_name)
        self.assertEqual(self.user.department, 'Marketing')
        self.assertEqual(self.user.job_title, 'Marketing Manager')
        self.assertNotEqual(self.user.first_name, original_name)
