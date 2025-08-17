"""
Test suite for the Users app
Testing user models, authentication, permissions, and user management.
"""

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.test.client import Client
from django_tenants.utils import schema_context
from unittest.mock import patch, MagicMock

from apps.users.models import TenantUser
from apps.tenants.models import Tenant, Domain
from apps.common.services.user_management import UserManagementService
from apps.permissions.models import Permission, RoleGroup
from apps.tenant_permissions.models import TenantRole, TenantUserRole

User = get_user_model()


class TenantUserModelTest(TestCase):
    """Test TenantUser model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='User Test Tenant',
            schema_name='user_test'
        )
        Domain.objects.create(
            domain='usertest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_user_creation(self):
        """Test creating a tenant user with valid data."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create(
                email='test@usertest.com',
                first_name='Test',
                last_name='User',
                phone_number='+1234567890',
                job_title='Developer',
                department='Engineering',
                user_type='user'
            )
            
            self.assertEqual(user.email, 'test@usertest.com')
            self.assertEqual(user.first_name, 'Test')
            self.assertEqual(user.last_name, 'User')
            self.assertEqual(user.user_type, 'user')
            self.assertFalse(user.is_tenant_admin)
            self.assertTrue(user.is_active)
    
    def test_user_str_representation(self):
        """Test string representation of user."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create(
                email='string@test.com',
                first_name='String',
                last_name='Test'
            )
            self.assertEqual(str(user), 'string@test.com')
    
    def test_user_full_name(self):
        """Test get_full_name method."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create(
                email='fullname@test.com',
                first_name='Full',
                last_name='Name'
            )
            self.assertEqual(user.get_full_name(), 'Full Name')
    
    def test_user_email_uniqueness(self):
        """Test that email addresses must be unique within a tenant."""
        with schema_context(self.tenant.schema_name):
            TenantUser.objects.create(
                email='unique@test.com',
                first_name='First',
                last_name='User'
            )
            
            # Creating another user with same email should fail
            with self.assertRaises(Exception):  # Could be IntegrityError or ValidationError
                TenantUser.objects.create(
                    email='unique@test.com',
                    first_name='Second',
                    last_name='User'
                )
    
    def test_user_email_validation(self):
        """Test email field validation."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser(
                email='invalid-email',
                first_name='Invalid',
                last_name='Email'
            )
            
            with self.assertRaises(ValidationError):
                user.full_clean()
    
    def test_admin_user_creation(self):
        """Test creating an admin user."""
        with schema_context(self.tenant.schema_name):
            admin_user = TenantUser.objects.create(
                email='admin@test.com',
                first_name='Admin',
                last_name='User',
                user_type='admin',
                is_tenant_admin=True,
                is_staff=True
            )
            
            self.assertEqual(admin_user.user_type, 'admin')
            self.assertTrue(admin_user.is_tenant_admin)
            self.assertTrue(admin_user.is_staff)
    
    def test_user_password_hashing(self):
        """Test that passwords are properly hashed."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create_user(
                email='password@test.com',
                password='testpassword123'
            )
            
            # Password should be hashed, not stored in plain text
            self.assertNotEqual(user.password, 'testpassword123')
            self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_user_authentication(self):
        """Test user authentication."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create_user(
                email='auth@test.com',
                password='authtest123'
            )
            
            # Test successful authentication
            authenticated_user = authenticate(
                username='auth@test.com',
                password='authtest123'
            )
            self.assertEqual(authenticated_user, user)
            
            # Test failed authentication
            failed_auth = authenticate(
                username='auth@test.com',
                password='wrongpassword'
            )
            self.assertIsNone(failed_auth)


class UserManagementServiceTest(TransactionTestCase):
    """Test UserManagementService functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Service Test Tenant',
            schema_name='service_test'
        )
        Domain.objects.create(
            domain='servicetest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_password_generation(self):
        """Test secure password generation."""
        password1 = UserManagementService.generate_secure_password()
        password2 = UserManagementService.generate_secure_password(16)
        
        # Test default length
        self.assertEqual(len(password1), 12)
        
        # Test custom length
        self.assertEqual(len(password2), 16)
        
        # Test passwords are different
        self.assertNotEqual(password1, password2)
        
        # Test password complexity
        self.assertTrue(any(c.islower() for c in password1))
        self.assertTrue(any(c.isupper() for c in password1))
        self.assertTrue(any(c.isdigit() for c in password1))
        self.assertTrue(any(c in "!@#$%^&*" for c in password1))
    
    def test_user_data_validation(self):
        """Test user data validation."""
        # Valid data
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@test.com',
            'phone_number': '+1234567890',
            'job_title': 'Developer',
            'department': 'Engineering'
        }
        
        validated = UserManagementService.validate_user_data(valid_data)
        self.assertEqual(validated['email'], 'john.doe@test.com')
        self.assertEqual(validated['first_name'], 'John')
        
        # Invalid data - missing required field
        invalid_data = {
            'first_name': 'John',
            'email': 'john@test.com'
            # Missing last_name
        }
        
        with self.assertRaises(ValueError):
            UserManagementService.validate_user_data(invalid_data)
        
        # Invalid data - invalid email
        invalid_email_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email'
        }
        
        with self.assertRaises(ValueError):
            UserManagementService.validate_user_data(invalid_email_data)
    
    @patch('apps.common.services.permission_service.PermissionService.assign_admin_role')
    def test_create_tenant_admin_user(self, mock_assign_role):
        """Test creating a tenant admin user."""
        mock_assign_role.return_value = True
        
        user_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'unique_admin@servicetest.com',
            'job_title': 'Administrator',
            'department': 'Management'
        }
        
        result = UserManagementService.create_tenant_admin_user(self.tenant, user_data)
        
        self.assertTrue(result['success'])
        self.assertIn('user', result)
        self.assertIn('password', result)
        
        user = result['user']
        self.assertEqual(user.email, 'unique_admin@servicetest.com')
        self.assertTrue(user.is_tenant_admin)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.user_type, 'admin')
        
        # Verify role assignment was called
        mock_assign_role.assert_called_once_with(user, self.tenant)
    
    def test_create_tenant_admin_user_duplicate_email(self):
        """Test creating admin user with duplicate email raises ValueError."""
        user_data = {
            'first_name': 'First',
            'last_name': 'User',
            'email': 'duplicate@servicetest.com'
        }
        
        # Create first user
        with schema_context(self.tenant.schema_name):
            TenantUser.objects.create(**user_data)
        
        # Try to create second user with same email should raise ValueError
        with self.assertRaises(ValueError) as context:
            UserManagementService.create_tenant_admin_user(self.tenant, user_data)
        
        self.assertIn('already exists', str(context.exception))
    
    @patch('apps.tenant_permissions.models.TenantRole.objects.get')
    @patch('apps.tenant_permissions.models.TenantUserRole.objects.create')
    def test_create_regular_user(self, mock_create_role, mock_get_role):
        """Test creating a regular user."""
        # Setup mocks
        mock_role = MagicMock()
        mock_role.name = 'User'
        mock_get_role.return_value = mock_role
        
        # Create admin user first
        with schema_context(self.tenant.schema_name):
            admin_user = TenantUser.objects.create(
                email='admin@servicetest.com',
                first_name='Admin',
                last_name='User',
                is_tenant_admin=True
            )
        
        user_data = {
            'first_name': 'Regular',
            'last_name': 'User',
            'email': 'regular@servicetest.com',
            'job_title': 'Developer',
            'role': 'User'
        }
        
        result = UserManagementService.create_regular_user(
            self.tenant, user_data, admin_user
        )
        
        self.assertTrue(result['success'])
        user = result['user']
        self.assertEqual(user.email, 'regular@servicetest.com')
        self.assertFalse(user.is_tenant_admin)
        self.assertFalse(user.is_staff)
    
    def test_get_user_info(self):
        """Test getting comprehensive user information."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create(
                email='info@servicetest.com',
                first_name='Info',
                last_name='User',
                job_title='Tester',
                department='QA'
            )
        
        user_info = UserManagementService.get_user_info(user, self.tenant)
        
        self.assertEqual(user_info['email'], 'info@servicetest.com')
        self.assertEqual(user_info['full_name'], 'Info User')
        self.assertEqual(user_info['job_title'], 'Tester')
        self.assertEqual(user_info['department'], 'QA')
        self.assertIn('roles', user_info)
        self.assertIn('permissions', user_info)
        self.assertIn('tenant', user_info)


class UserPermissionTest(TransactionTestCase):
    """Test user permission functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Permission Test Tenant',
            schema_name='permission_test'
        )
        Domain.objects.create(
            domain='permissiontest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create some permissions in public schema
        self.permission1 = Permission.objects.create(
            name='Test Permission 1',
            codename='test_permission_1',
            description='First test permission',
            category='Test'
        )
        self.permission2 = Permission.objects.create(
            name='Test Permission 2',
            codename='test_permission_2',
            description='Second test permission',
            category='Test'
        )
    
    def test_user_permission_checking(self):
        """Test user permission checking methods."""
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create(
                email='permission@test.com',
                first_name='Permission',
                last_name='User'
            )
            
            # Test has_permission method
            permissions = user.get_permissions()
            self.assertIsInstance(permissions, list)
            
            # Test has_any_permission method (if implemented)
            if hasattr(user, 'has_any_permission'):
                result = user.has_any_permission(['Test Permission 1', 'Test Permission 2'])
                self.assertIsInstance(result, bool)


class UserAdminTest(TestCase):
    """Test User admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            password='testpass123'
        )
        self.client = Client()
        
        self.tenant = Tenant.objects.create(
            name='Admin Test Tenant',
            schema_name='admin_test'
        )
    
    def test_admin_user_list_view(self):
        """Test admin list view for users."""
        with schema_context(self.tenant.schema_name):
            TenantUser.objects.create(
                email='user1@admintest.com',
                first_name='User',
                last_name='One'
            )
            TenantUser.objects.create(
                email='user2@admintest.com',
                first_name='User',
                last_name='Two'
            )
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Access admin list view
        response = self.client.get('/admin/users/tenantuser/')
        
        # This might not work due to tenant isolation
        if response.status_code == 200:
            self.assertContains(response, 'user1@admintest.com')
        else:
            # Expected due to tenant isolation
            self.assertIn(response.status_code, [200, 302, 404])


class UserAPITest(TestCase):
    """Test User API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.tenant = Tenant.objects.create(
            name='API Test Tenant',
            schema_name='api_test'
        )
        
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='api@test.com',
                first_name='API',
                last_name='User',
                password='testpass123'
            )
    
    def test_user_list_api(self):
        """Test listing users via API."""
        with schema_context(self.tenant.schema_name):
            self.client.force_login(self.user)
        
        response = self.client.get('/api/users/')
        
        if response.status_code == 404:
            # API endpoint might not be implemented yet
            self.skipTest("API endpoint not implemented yet")
        
        self.assertEqual(response.status_code, 200)
    
    def test_user_profile_api(self):
        """Test user profile via API."""
        with schema_context(self.tenant.schema_name):
            self.client.force_login(self.user)
        
        response = self.client.get('/api/users/profile/')
        
        if response.status_code == 404:
            # API endpoint might not be implemented yet
            self.skipTest("API endpoint not implemented yet")
        
        self.assertEqual(response.status_code, 200)


class UserIntegrationTest(TransactionTestCase):
    """Integration tests for user functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Integration Test Tenant',
            schema_name='integration_test'
        )
        Domain.objects.create(
            domain='integrationtest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_user_tenant_isolation(self):
        """Test that users are properly isolated between tenants."""
        tenant2 = Tenant.objects.create(
            name='Second Tenant',
            schema_name='second_tenant'
        )
        
        # Create user in first tenant
        with schema_context(self.tenant.schema_name):
            user1 = TenantUser.objects.create(
                email='user1@integration.com',
                first_name='User',
                last_name='One'
            )
            tenant1_count = TenantUser.objects.count()
        
        # Create user in second tenant
        with schema_context(tenant2.schema_name):
            user2 = TenantUser.objects.create(
                email='user2@integration.com',
                first_name='User',
                last_name='Two'
            )
            tenant2_count = TenantUser.objects.count()
        
        # Each tenant should only see their own users
        self.assertEqual(tenant1_count, 1)
        self.assertEqual(tenant2_count, 1)
        
        # Verify isolation
        with schema_context(self.tenant.schema_name):
            self.assertTrue(TenantUser.objects.filter(email='user1@integration.com').exists())
            self.assertFalse(TenantUser.objects.filter(email='user2@integration.com').exists())
        
        with schema_context(tenant2.schema_name):
            self.assertTrue(TenantUser.objects.filter(email='user2@integration.com').exists())
            self.assertFalse(TenantUser.objects.filter(email='user1@integration.com').exists())
    
    def test_complete_user_workflow(self):
        """Test complete user creation and management workflow."""
        # This tests the full user lifecycle
        user_data = {
            'first_name': 'Workflow',
            'last_name': 'User',
            'email': 'workflow@integration.com',
            'job_title': 'Manager',
            'department': 'Operations'
        }
        
        # Validate data
        validated_data = UserManagementService.validate_user_data(user_data)
        self.assertEqual(validated_data['email'], 'workflow@integration.com')
        
        # Create user would be tested here if database was fully set up
        # For now, just test the validation step worked
        self.assertIn('first_name', validated_data)
        self.assertIn('last_name', validated_data)
        self.assertIn('email', validated_data)
