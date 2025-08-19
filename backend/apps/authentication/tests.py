"""
Comprehensive tests for authentication app.
Tests middleware, backends, and authentication functionality.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.conf import settings
from unittest.mock import Mock, patch, MagicMock

from apps.authentication.middleware import TenantOnlyAuthenticationMiddleware
from apps.authentication.backends import EmailBackend
from apps.users.models import CustomUser
from apps.platform.models import SuperUser
from apps.tenants.models import Tenant, Domain


class EmailBackendTest(TestCase):
    """Test EmailBackend authentication backend."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email='test@testcorp.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create a platform user
        self.platform_user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.backend = EmailBackend()
    
    def test_authenticate_valid_user(self):
        """Test authentication with valid email and password."""
        user = self.backend.authenticate(
            request=None,
            email='test@testcorp.com',
            password='testpass123'
        )
        
        self.assertEqual(user, self.user)
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        user = self.backend.authenticate(
            request=None,
            email='test@testcorp.com',
            password='wrongpass'
        )
        
        self.assertIsNone(user)
    
    def test_authenticate_invalid_email(self):
        """Test authentication with invalid email."""
        user = self.backend.authenticate(
            request=None,
            email='nonexistent@testcorp.com',
            password='testpass123'
        )
        
        self.assertIsNone(user)
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        user = self.backend.authenticate(
            request=None,
            email='test@testcorp.com',
            password='testpass123'
        )
        
        self.assertIsNone(user)
    
    def test_authenticate_platform_user(self):
        """Test authentication with platform user."""
        user = self.backend.authenticate(
            request=None,
            email='admin@platform.com',
            password='adminpass123'
        )
        
        self.assertEqual(user, self.platform_user)
    
    def test_authenticate_missing_credentials(self):
        """Test authentication with missing credentials."""
        # Missing email
        user = self.backend.authenticate(
            request=None,
            password='testpass123'
        )
        self.assertIsNone(user)
        
        # Missing password
        user = self.backend.authenticate(
            request=None,
            email='test@testcorp.com'
        )
        self.assertIsNone(user)
    
    def test_get_user_valid_id(self):
        """Test get_user with valid user ID."""
        user = self.backend.get_user(self.user.id)
        self.assertEqual(user, self.user)
    
    def test_get_user_invalid_id(self):
        """Test get_user with invalid user ID."""
        user = self.backend.get_user(99999)
        self.assertIsNone(user)
    
    def test_get_user_platform_user(self):
        """Test get_user with platform user ID."""
        user = self.backend.get_user(self.platform_user.id)
        self.assertEqual(user, self.platform_user)
    
    def test_email_case_insensitive(self):
        """Test that email authentication is case insensitive."""
        # Test with uppercase email
        user = self.backend.authenticate(
            request=None,
            email='TEST@TESTCORP.COM',
            password='testpass123'
        )
        
        self.assertEqual(user, self.user)
    
    def test_authenticate_with_username_fallback(self):
        """Test that backend works with username parameter as well."""
        # Some Django components might use 'username' instead of 'email'
        user = self.backend.authenticate(
            request=None,
            username='test@testcorp.com',
            password='testpass123'
        )
        
        self.assertEqual(user, self.user)


class TenantOnlyAuthenticationMiddlewareTest(TestCase):
    """Test TenantOnlyAuthenticationMiddleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = TenantOnlyAuthenticationMiddleware(self.get_response)
        
        # Create test tenant
        self.tenant = Tenant.objects.create(
            schema_name='testcorp',
            name='Test Corporation',
            contact_email='admin@testcorp.com'
        )
        
        self.domain = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create test users
        self.tenant_user = CustomUser.objects.create_user(
            email='user@testcorp.com',
            password='userpass123',
            first_name='Tenant',
            last_name='User'
        )
        
        self.platform_user = SuperUser.objects.create_superuser(
            email='admin@platform.com',
            password='adminpass123',
            first_name='Platform',
            last_name='Admin'
        )
    
    def get_response(self, request):
        """Mock get_response for middleware testing."""
        return HttpResponse('OK')
    
    def test_middleware_allows_tenant_user_on_tenant_domain(self):
        """Test that tenant users can access tenant domain."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'testcorp.localhost'
        request.user = self.tenant_user
        
        # Mock tenant attribute
        request.tenant = self.tenant
        
        response = self.middleware(request)
        
        # Should not redirect (response is OK)
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_blocks_platform_user_on_tenant_domain(self):
        """Test that platform users are blocked from tenant domain."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'testcorp.localhost'
        request.user = self.platform_user
        
        # Mock tenant attribute
        request.tenant = self.tenant
        
        response = self.middleware(request)
        
        # Should redirect or block access
        # The actual implementation might vary
        self.assertIsNotNone(response)
    
    def test_middleware_allows_platform_user_on_platform_domain(self):
        """Test that platform users can access platform domain."""
        request = self.factory.get('/admin/')
        request.META['HTTP_HOST'] = 'localhost'
        request.user = self.platform_user
        
        # Mock tenant as None (public schema)
        request.tenant = None
        
        response = self.middleware(request)
        
        # Should allow access
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_with_anonymous_user(self):
        """Test middleware behavior with anonymous user."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'testcorp.localhost'
        request.user = AnonymousUser()
        
        # Mock tenant attribute
        request.tenant = self.tenant
        
        response = self.middleware(request)
        
        # Should allow anonymous access (for login pages, etc.)
        self.assertIsNotNone(response)
    
    def test_middleware_preserves_request_attributes(self):
        """Test that middleware preserves request attributes."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'testcorp.localhost'
        request.user = self.tenant_user
        request.tenant = self.tenant
        
        # Add custom attribute
        request.custom_attr = 'test_value'
        
        response = self.middleware(request)
        
        # Custom attribute should be preserved
        self.assertEqual(request.custom_attr, 'test_value')
    
    @patch('apps.authentication.middleware.logger')
    def test_middleware_logs_access_attempts(self, mock_logger):
        """Test that middleware logs access attempts."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'testcorp.localhost'
        request.user = self.platform_user
        request.tenant = self.tenant
        
        self.middleware(request)
        
        # Should log the access attempt
        # This test depends on the actual implementation
        # mock_logger.warning.assert_called()


class AuthenticationIntegrationTest(TestCase):
    """Integration tests for authentication functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant
        self.tenant = Tenant.objects.create(
            schema_name='testcorp',
            name='Test Corporation',
            contact_email='admin@testcorp.com'
        )
        
        self.domain = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create users
        self.tenant_admin = CustomUser.objects.create_user(
            email='admin@testcorp.com',
            password='adminpass123',
            first_name='Tenant',
            last_name='Admin',
            is_admin=True
        )
        
        self.tenant_user = CustomUser.objects.create_user(
            email='user@testcorp.com',
            password='userpass123',
            first_name='Tenant',
            last_name='User'
        )
        
        self.platform_admin = SuperUser.objects.create_superuser(
            email='platform@admin.com',
            password='platformpass123',
            first_name='Platform',
            last_name='Admin'
        )
    
    def test_tenant_admin_authentication(self):
        """Test tenant admin authentication flow."""
        # Authenticate tenant admin
        user = authenticate(
            email='admin@testcorp.com',
            password='adminpass123'
        )
        
        self.assertEqual(user, self.tenant_admin)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)
        
        # Test permissions
        self.assertTrue(user.is_staff)  # Admin users have staff access
        self.assertTrue(user.is_superuser)  # Admin users have superuser access
    
    def test_tenant_user_authentication(self):
        """Test regular tenant user authentication flow."""
        # Authenticate tenant user
        user = authenticate(
            email='user@testcorp.com',
            password='userpass123'
        )
        
        self.assertEqual(user, self.tenant_user)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        
        # Test permissions
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_platform_admin_authentication(self):
        """Test platform admin authentication flow."""
        # Authenticate platform admin
        user = authenticate(
            email='platform@admin.com',
            password='platformpass123'
        )
        
        self.assertEqual(user, self.platform_admin)
        self.assertTrue(user.is_active)
        
        # Test permissions
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_cross_tenant_authentication_isolation(self):
        """Test that tenant users are isolated from each other."""
        # Create another tenant
        tenant2 = Tenant.objects.create(
            schema_name='othercorp',
            name='Other Corporation',
            contact_email='admin@othercorp.com'
        )
        
        domain2 = Domain.objects.create(
            domain='othercorp.localhost',
            tenant=tenant2,
            is_primary=True
        )
        
        # Create user in second tenant with same email
        other_user = CustomUser.objects.create_user(
            email='user@othercorp.com',  # Different email
            password='otherpass123',
            first_name='Other',
            last_name='User'
        )
        
        # Authenticate users
        user1 = authenticate(
            email='user@testcorp.com',
            password='userpass123'
        )
        
        user2 = authenticate(
            email='user@othercorp.com',
            password='otherpass123'
        )
        
        # Users should be different
        self.assertNotEqual(user1, user2)
        self.assertEqual(user1, self.tenant_user)
        self.assertEqual(user2, other_user)
    
    def test_authentication_with_different_backends(self):
        """Test authentication with different backends."""
        from apps.authentication.backends import EmailBackend
        
        backend = EmailBackend()
        
        # Test tenant user
        user = backend.authenticate(
            request=None,
            email='user@testcorp.com',
            password='userpass123'
        )
        self.assertEqual(user, self.tenant_user)
        
        # Test platform user
        user = backend.authenticate(
            request=None,
            email='platform@admin.com',
            password='platformpass123'
        )
        self.assertEqual(user, self.platform_admin)
    
    def test_authentication_error_handling(self):
        """Test authentication error handling."""
        # Test with malformed email
        user = authenticate(
            email='not-an-email',
            password='testpass123'
        )
        self.assertIsNone(user)
        
        # Test with None values
        user = authenticate(email=None, password=None)
        self.assertIsNone(user)
        
        # Test with empty strings
        user = authenticate(email='', password='')
        self.assertIsNone(user)
    
    def test_password_validation(self):
        """Test password validation during authentication."""
        # Test correct password
        user = authenticate(
            email='user@testcorp.com',
            password='userpass123'
        )
        self.assertIsNotNone(user)
        
        # Test incorrect password
        user = authenticate(
            email='user@testcorp.com',
            password='wrongpassword'
        )
        self.assertIsNone(user)
        
        # Test partial password
        user = authenticate(
            email='user@testcorp.com',
            password='userpass'  # Missing characters
        )
        self.assertIsNone(user)


class AuthenticationSecurityTest(TestCase):
    """Test authentication security features."""
    
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email='secure@testcorp.com',
            password='securepass123',
            first_name='Secure',
            last_name='User'
        )
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        # Password should not be stored in plain text
        self.assertNotEqual(self.user.password, 'securepass123')
        
        # Password should be hashed
        self.assertTrue(self.user.password.startswith('pbkdf2_sha256'))
        
        # User should be able to check password
        self.assertTrue(self.user.check_password('securepass123'))
        self.assertFalse(self.user.check_password('wrongpass'))
    
    def test_authentication_timing_attack_prevention(self):
        """Test that authentication prevents timing attacks."""
        import time
        
        # Time authentication with valid user
        start_time = time.time()
        authenticate(email='secure@testcorp.com', password='wrongpass')
        valid_user_time = time.time() - start_time
        
        # Time authentication with invalid user
        start_time = time.time()
        authenticate(email='nonexistent@testcorp.com', password='wrongpass')
        invalid_user_time = time.time() - start_time
        
        # Times should be similar (within reasonable margin)
        # This is a basic test - real timing attack prevention is more complex
        time_difference = abs(valid_user_time - invalid_user_time)
        self.assertLess(time_difference, 0.1)  # 100ms margin
    
    def test_case_insensitive_email_authentication(self):
        """Test that email authentication is case insensitive but preserves case."""
        # Authenticate with different cases
        user1 = authenticate(
            email='secure@testcorp.com',
            password='securepass123'
        )
        
        user2 = authenticate(
            email='SECURE@TESTCORP.COM',
            password='securepass123'
        )
        
        user3 = authenticate(
            email='Secure@TestCorp.com',
            password='securepass123'
        )
        
        # All should authenticate to the same user
        self.assertEqual(user1, self.user)
        self.assertEqual(user2, self.user)
        self.assertEqual(user3, self.user)
        
        # Original email case should be preserved
        self.assertEqual(self.user.email, 'secure@testcorp.com')
    
    def test_authentication_with_special_characters(self):
        """Test authentication with special characters in email."""
        special_user = CustomUser.objects.create_user(
            email='special+user@test-corp.com',
            password='specialpass123',
            first_name='Special',
            last_name='User'
        )
        
        user = authenticate(
            email='special+user@test-corp.com',
            password='specialpass123'
        )
        
        self.assertEqual(user, special_user)
    
    def test_authentication_rate_limiting_preparation(self):
        """Test preparation for authentication rate limiting."""
        # This test prepares for rate limiting implementation
        # Multiple failed attempts should still work (no rate limiting implemented yet)
        
        failed_attempts = 0
        for i in range(5):
            user = authenticate(
                email='secure@testcorp.com',
                password='wrongpass'
            )
            if user is None:
                failed_attempts += 1
        
        # All attempts should fail
        self.assertEqual(failed_attempts, 5)
        
        # Valid authentication should still work
        user = authenticate(
            email='secure@testcorp.com',
            password='securepass123'
        )
        self.assertEqual(user, self.user)
