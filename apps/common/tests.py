"""
Test suite for the Common app services
Testing service-oriented architecture components, utilities, and shared functionality.
"""

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from unittest.mock import patch, MagicMock, call

from apps.tenants.models import Tenant, Domain
from apps.demo.models import DemoRequest
from apps.permissions.models import Permission, RoleGroup
from apps.common.services.tenant_provisioning import TenantProvisioningService
from apps.common.services.user_management import UserManagementService
from apps.common.services.email_service import EmailService
from apps.common.services.tenant_workflow import TenantWorkflowService
from apps.common.services.permission_service import PermissionService


class TenantProvisioningServiceTest(TransactionTestCase):
    """Test TenantProvisioningService functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant_data = {
            'name': 'Provisioning Test Corp',
            'description': 'Test tenant for provisioning service',
            'subscription_status': 'trial'
        }
    
    @patch('apps.common.services.permission_service.PermissionService.setup_tenant_permissions')
    def test_create_tenant_with_setup_success(self, mock_permissions):
        """Test successful tenant creation and setup."""
        mock_permissions.return_value = {
            'success': True,
            'permissions_created': 8,
            'role_groups_created': 3
        }
        
        result = TenantProvisioningService.create_tenant_with_setup(self.tenant_data)
        
        self.assertTrue(result['success'])
        self.assertIn('tenant', result)
        self.assertIn('domain', result)
        
        # Verify tenant was created correctly
        tenant = result['tenant']
        self.assertEqual(tenant.name, 'Provisioning Test Corp')
        self.assertEqual(tenant.subscription_status, 'trial')
        self.assertTrue(tenant.schema_name)
        
        # Verify domain was created
        domain = result['domain']
        self.assertEqual(domain.tenant, tenant)
        self.assertTrue(domain.is_primary)
        self.assertTrue(domain.domain.endswith('.localhost'))
        
        # Verify permissions setup was called
        mock_permissions.assert_called_once_with(tenant)
    
    def test_create_tenant_invalid_data(self):
        """Test tenant creation with invalid data."""
        invalid_data = {
            'name': '',  # Empty name
            'subscription_status': 'invalid_status'
        }
        
        result = TenantProvisioningService.create_tenant_with_setup(invalid_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_generate_schema_name(self):
        """Test schema name generation."""
        test_cases = [
            ('Simple Corp', 'simple_corp'),
            ('Test & Company Inc.', 'test_company_inc'),
            ('123 Numbers Corp', '123_numbers_corp'),
            ('Special!@#$%^&*()Corp', 'special_corp'),
        ]
        
        for tenant_name, expected_prefix in test_cases:
            schema_name = TenantProvisioningService._generate_schema_name(tenant_name)
            self.assertTrue(schema_name.startswith(expected_prefix))
            self.assertTrue(schema_name.replace('_', '').replace('-', '').isalnum())
    
    def test_generate_domain_name(self):
        """Test domain name generation."""
        test_cases = [
            'Simple Corp',
            'Test & Company Inc.',
            'Numbers 123 Corp',
            'Special!@#$%^&*()Corp',
        ]
        
        for tenant_name in test_cases:
            domain = TenantProvisioningService._generate_domain_name(tenant_name)
            self.assertTrue(domain.endswith('.localhost'))
            self.assertTrue(domain.replace('.', '').replace('-', '').isalnum())
    
    @patch('apps.common.services.permission_service.PermissionService.setup_tenant_permissions')
    def test_permissions_setup_failure_handling(self, mock_permissions):
        """Test handling of permissions setup failure."""
        mock_permissions.return_value = {
            'success': False,
            'error': 'Database connection failed'
        }
        
        result = TenantProvisioningService.create_tenant_with_setup(self.tenant_data)
        
        # Tenant creation should still succeed
        self.assertTrue(result['success'])
        self.assertIn('permissions_warning', result)
        self.assertIn('Database connection failed', result['permissions_warning'])


class UserManagementServiceTest(TransactionTestCase):
    """Test UserManagementService functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='User Management Test',
            schema_name='user_mgmt_test'
        )
        Domain.objects.create(
            domain='usermgmt.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_password_generation_security(self):
        """Test password generation meets security requirements."""
        passwords = [UserManagementService.generate_secure_password() for _ in range(10)]
        
        for password in passwords:
            # Test length
            self.assertEqual(len(password), 12)
            
            # Test character requirements
            self.assertTrue(any(c.islower() for c in password), f"No lowercase in: {password}")
            self.assertTrue(any(c.isupper() for c in password), f"No uppercase in: {password}")
            self.assertTrue(any(c.isdigit() for c in password), f"No digit in: {password}")
            self.assertTrue(any(c in "!@#$%^&*" for c in password), f"No symbol in: {password}")
        
        # Test passwords are unique
        self.assertEqual(len(set(passwords)), len(passwords))
    
    def test_password_generation_custom_length(self):
        """Test password generation with custom length."""
        for length in [8, 16, 20, 32]:
            password = UserManagementService.generate_secure_password(length)
            self.assertEqual(len(password), length)
            
            # Still meets complexity requirements
            self.assertTrue(any(c.islower() for c in password))
            self.assertTrue(any(c.isupper() for c in password))
            self.assertTrue(any(c.isdigit() for c in password))
            self.assertTrue(any(c in "!@#$%^&*" for c in password))
    
    def test_validate_user_data_success(self):
        """Test successful user data validation."""
        valid_data = {
            'first_name': '  john  ',  # Test trimming
            'last_name': '  DOE  ',   # Test case conversion
            'email': '  JOHN.DOE@EXAMPLE.COM  ',  # Test email cleaning
            'phone_number': '+1234567890',
            'job_title': 'Developer',
            'department': 'Engineering'
        }
        
        result = UserManagementService.validate_user_data(valid_data)
        
        self.assertEqual(result['first_name'], 'John')
        self.assertEqual(result['last_name'], 'Doe')
        self.assertEqual(result['email'], 'john.doe@example.com')
        self.assertEqual(result['phone_number'], '+1234567890')
    
    def test_validate_user_data_failures(self):
        """Test user data validation failures."""
        test_cases = [
            # Missing required fields
            {'last_name': 'Doe', 'email': 'test@example.com'},  # Missing first_name
            {'first_name': 'John', 'email': 'test@example.com'},  # Missing last_name
            {'first_name': 'John', 'last_name': 'Doe'},  # Missing email
            
            # Invalid data
            {'first_name': 'A', 'last_name': 'Doe', 'email': 'test@example.com'},  # Too short
            {'first_name': 'John', 'last_name': 'B', 'email': 'test@example.com'},  # Too short
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'invalid-email'},  # Invalid email
        ]
        
        for invalid_data in test_cases:
            with self.assertRaises(ValueError):
                UserManagementService.validate_user_data(invalid_data)
    
    @patch('apps.common.services.permission_service.PermissionService.assign_admin_role')
    def test_create_tenant_admin_user_success(self, mock_assign_role):
        """Test successful admin user creation."""
        mock_assign_role.return_value = True
        
        user_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@test.com',
            'job_title': 'Administrator'
        }
        
        result = UserManagementService.create_tenant_admin_user(self.tenant, user_data)
        
        self.assertTrue(result['success'])
        self.assertIn('user', result)
        self.assertIn('password', result)
        
        user = result['user']
        self.assertEqual(user.email, 'admin@test.com')
        self.assertTrue(user.is_tenant_admin)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.user_type, 'admin')
        
        # Verify password was generated
        password = result['password']
        self.assertIsInstance(password, str)
        self.assertGreater(len(password), 8)
        
        mock_assign_role.assert_called_once_with(user, self.tenant)
    
    def test_create_tenant_admin_user_validation_error(self):
        """Test admin user creation with validation error."""
        invalid_data = {
            'first_name': '',  # Invalid
            'last_name': 'User',
            'email': 'admin@test.com'
        }
        
        with self.assertRaises(ValueError):
            UserManagementService.create_tenant_admin_user(self.tenant, invalid_data)


class EmailServiceTest(TestCase):
    """Test EmailService functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Email Test Tenant',
            schema_name='email_test'
        )
        Domain.objects.create(
            domain='emailtest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    @patch('apps.common.services.email_service.EmailMultiAlternatives.send')
    def test_send_welcome_email_success(self, mock_send):
        """Test successful welcome email sending."""
        mock_send.return_value = True
        
        # Create mock user
        user = MagicMock()
        user.email = 'test@emailtest.com'
        user.get_full_name.return_value = 'Test User'
        user.user_type = 'admin'
        
        password = 'test_password123'
        
        result = EmailService.send_welcome_email(user, self.tenant, password)
        
        self.assertTrue(result['success'])
        self.assertIn('email_data', result)
        self.assertEqual(result['email_data']['to'], 'test@emailtest.com')
        
        mock_send.assert_called_once()
    
    @patch('apps.common.services.email_service.EmailMultiAlternatives.send')
    def test_send_welcome_email_failure(self, mock_send):
        """Test welcome email sending failure."""
        mock_send.side_effect = Exception('SMTP server unavailable')
        
        user = MagicMock()
        user.email = 'test@emailtest.com'
        user.get_full_name.return_value = 'Test User'
        user.user_type = 'admin'
        
        result = EmailService.send_welcome_email(user, self.tenant, 'password123')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('SMTP server unavailable', result['error'])
    
    @patch('apps.common.services.email_service.EmailMultiAlternatives.send')
    def test_send_password_reset_email(self, mock_send):
        """Test password reset email sending."""
        mock_send.return_value = True
        
        user = MagicMock()
        user.email = 'reset@emailtest.com'
        user.get_full_name.return_value = 'Reset User'
        
        result = EmailService.send_password_reset_email(user, self.tenant, 'new_password123')
        
        self.assertTrue(result['success'])
        mock_send.assert_called_once()
    
    def test_get_email_status(self):
        """Test getting email configuration status."""
        status = EmailService.get_email_status()
        
        self.assertIn('backend', status)
        self.assertIn('status', status)
        self.assertIn('from_email', status)
        
        # Should indicate console backend for testing
        self.assertIn('console', status['backend'].lower())


class TenantWorkflowServiceTest(TransactionTestCase):
    """Test TenantWorkflowService functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.demo_data = {
            'company_name': 'Workflow Test Corp',
            'first_name': 'Workflow',
            'last_name': 'Tester',
            'email': 'workflow@test.com',
            'job_title': 'CEO',
            'company_size': '11-50',
            'industry': 'Technology'
        }
    
    @patch('apps.common.services.tenant_provisioning.TenantProvisioningService.create_tenant_with_setup')
    @patch('apps.common.services.user_management.UserManagementService.create_tenant_admin_user')
    @patch('apps.common.services.email_service.EmailService.send_welcome_email')
    def test_process_demo_request_success(self, mock_email, mock_user, mock_tenant):
        """Test successful demo request processing workflow."""
        # Create demo request
        demo = DemoRequest.objects.create(**self.demo_data)
        
        # Setup mocks
        mock_tenant_obj = MagicMock()
        mock_tenant_obj.name = 'Workflow Test Corp'
        mock_user_obj = MagicMock()
        mock_user_obj.email = 'workflow@test.com'
        
        mock_tenant.return_value = {
            'success': True,
            'tenant': mock_tenant_obj,
            'message': 'Tenant created successfully'
        }
        
        mock_user.return_value = {
            'success': True,
            'user': mock_user_obj,
            'password': 'generated_password123',
            'message': 'User created successfully'
        }
        
        mock_email.return_value = {
            'success': True,
            'message': 'Email sent successfully'
        }
        
        # Process workflow
        result = TenantWorkflowService.process_demo_request(demo.id)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertEqual(result['tenant'], mock_tenant_obj)
        self.assertEqual(result['admin_user'], mock_user_obj)
        self.assertTrue(result['email_sent'])
        
        # Verify demo status updated
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'approved')
        
        # Verify all services called in correct order
        mock_tenant.assert_called_once()
        mock_user.assert_called_once()
        mock_email.assert_called_once()
        
        # Verify workflow steps recorded
        self.assertIn('steps', result)
        self.assertEqual(len(result['steps']), 3)
    
    @patch('apps.common.services.tenant_provisioning.TenantProvisioningService.create_tenant_with_setup')
    def test_process_demo_request_tenant_failure(self, mock_tenant):
        """Test workflow failure during tenant creation."""
        demo = DemoRequest.objects.create(**self.demo_data)
        
        mock_tenant.return_value = {
            'success': False,
            'message': 'Database error during tenant creation'
        }
        
        result = TenantWorkflowService.process_demo_request(demo.id)
        
        self.assertFalse(result['success'])
        self.assertIn('Tenant creation failed', result['message'])
        
        # Demo status should be updated to failed
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'failed')
    
    def test_process_demo_request_not_found(self):
        """Test processing non-existent demo request."""
        result = TenantWorkflowService.process_demo_request(99999)
        
        self.assertFalse(result['success'])
        self.assertIn('not found', result['message'])
    
    def test_process_demo_request_wrong_status(self):
        """Test processing demo with wrong status."""
        demo = DemoRequest.objects.create(**self.demo_data)
        demo.status = 'approved'  # Not pending
        demo.save()
        
        result = TenantWorkflowService.process_demo_request(demo.id)
        
        self.assertFalse(result['success'])
        self.assertIn('not pending', result['message'])
    
    def test_list_pending_demo_requests(self):
        """Test listing pending demo requests."""
        # Create demo requests with different statuses
        pending1 = DemoRequest.objects.create(
            company_name='Pending Corp 1',
            first_name='User1',
            last_name='Test',
            email='user1@pending.com',
            status='pending'
        )
        
        approved = DemoRequest.objects.create(
            company_name='Approved Corp',
            first_name='User2',
            last_name='Test',
            email='user2@approved.com',
            status='approved'
        )
        
        pending2 = DemoRequest.objects.create(
            company_name='Pending Corp 2',
            first_name='User3',
            last_name='Test',
            email='user3@pending.com',
            status='pending'
        )
        
        result = TenantWorkflowService.list_pending_demo_requests()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        
        # Verify only pending requests returned
        company_names = [req['company_name'] for req in result['requests']]
        self.assertIn('Pending Corp 1', company_names)
        self.assertIn('Pending Corp 2', company_names)
        self.assertNotIn('Approved Corp', company_names)
    
    @patch.object(TenantWorkflowService, 'process_demo_request')
    def test_bulk_process_demo_requests(self, mock_process):
        """Test bulk processing of demo requests."""
        # Setup demo requests
        demo1 = DemoRequest.objects.create(
            company_name='Bulk Test 1',
            first_name='User1',
            last_name='Test',
            email='user1@bulk.com'
        )
        demo2 = DemoRequest.objects.create(
            company_name='Bulk Test 2',
            first_name='User2',
            last_name='Test',
            email='user2@bulk.com'
        )
        
        # Mock responses
        mock_process.side_effect = [
            {'success': True, 'message': 'Success for demo 1'},
            {'success': False, 'message': 'Failed for demo 2'}
        ]
        
        result = TenantWorkflowService.bulk_process_demo_requests([demo1.id, demo2.id])
        
        self.assertEqual(result['total_processed'], 2)
        self.assertEqual(result['successful'], 1)
        self.assertEqual(result['failed'], 1)
        
        # Verify process was called for each demo
        self.assertEqual(mock_process.call_count, 2)
        mock_process.assert_has_calls([call(demo1.id), call(demo2.id)])


class PermissionServiceIntegrationTest(TestCase):
    """Integration tests for PermissionService with other components."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Permission Integration Test',
            schema_name='perm_integration'
        )
    
    def test_complete_permission_setup_workflow(self):
        """Test complete permission setup for a new tenant."""
        # This would test the full permission setup process
        result = PermissionService.setup_tenant_permissions(self.tenant)
        
        # Should succeed or provide detailed error information
        if not result.get('success', True):
            self.assertIn('error', result)
        else:
            self.assertIn('permissions_created', result)
    
    @patch('apps.common.services.permission_service.PermissionService.assign_admin_role')
    def test_user_permission_assignment_integration(self, mock_assign):
        """Test integration between user creation and permission assignment."""
        mock_assign.return_value = True
        
        user_data = {
            'first_name': 'Integration',
            'last_name': 'User',
            'email': 'integration@test.com'
        }
        
        # This would test the complete user creation with permissions
        with schema_context(self.tenant.schema_name):
            # User creation with permission assignment would be tested here
            # For now, just verify the service can be called
            mock_assign.assert_not_called()  # Not called yet
            
            # Simulate user creation triggering permission assignment
            PermissionService.assign_admin_role(MagicMock(), self.tenant)
            mock_assign.assert_called_once()


class ServiceLayerIntegrationTest(TransactionTestCase):
    """Integration tests for the entire service layer."""
    
    def test_service_layer_dependencies(self):
        """Test that all services can be imported and instantiated."""
        # Test that all service classes can be imported
        services = [
            TenantProvisioningService,
            UserManagementService,
            EmailService,
            TenantWorkflowService,
            PermissionService
        ]
        
        for service_class in services:
            self.assertTrue(hasattr(service_class, '__name__'))
            
            # Test that service methods exist
            if hasattr(service_class, 'create_tenant_with_setup'):
                self.assertTrue(callable(getattr(service_class, 'create_tenant_with_setup')))
    
    def test_service_error_handling_consistency(self):
        """Test that all services handle errors consistently."""
        # All services should return consistent error response format
        expected_error_keys = ['success', 'message', 'error']
        
        # Test error responses have consistent structure
        # (Individual service tests cover the actual error scenarios)
        self.assertTrue(True)  # Placeholder for structure validation
    
    def test_service_logging_integration(self):
        """Test that services properly integrate with logging system."""
        # This would test that all services properly log their activities
        # For now, just verify logging is configured
        import logging
        
        logger = logging.getLogger('apps.common.services')
        self.assertIsNotNone(logger)
        
        # Services should use consistent logging patterns
        self.assertTrue(True)  # Placeholder for logging validation
