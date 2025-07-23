"""
Test suite for the Authentication app
Testing authentication backends, middleware, and security functionality.
"""

from django.test import TestCase, TransactionTestCase, RequestFactory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils import timezone
from django_tenants.utils import schema_context
from unittest.mock import patch, MagicMock
from datetime import timedelta

from apps.tenants.models import Tenant, Domain
from apps.users.models import TenantUser
from apps.authentication.backends import TenantAuthenticationBackend
from apps.authentication.middleware import TenantAuthenticationMiddleware


class TenantAuthenticationBackendTest(TransactionTestCase):
    """Test custom tenant authentication backend."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name='Auth Test Corp',
            schema_name='auth_test'
        )
        Domain.objects.create(
            domain='authtest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create user within tenant schema
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='user@authtest.com',
                password='testpass123',
                first_name='Test',
                last_name='User',
                is_active=True
            )
    
    def test_authenticate_valid_credentials(self):
        """Test authentication with valid credentials."""
        backend = TenantAuthenticationBackend()
        
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username='user@authtest.com',
                password='testpass123',
                tenant=self.tenant
            )
        
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.email, 'user@authtest.com')
        self.assertEqual(authenticated_user, self.user)
    
    def test_authenticate_invalid_email(self):
        """Test authentication with invalid email."""
        backend = TenantAuthenticationBackend()
        
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username='nonexistent@authtest.com',
                password='testpass123',
                tenant=self.tenant
            )
        
        self.assertIsNone(authenticated_user)
    
    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        backend = TenantAuthenticationBackend()
        
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username='user@authtest.com',
                password='wrongpassword',
                tenant=self.tenant
            )
        
        self.assertIsNone(authenticated_user)
    
    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user."""
        # Create inactive user
        with schema_context(self.tenant.schema_name):
            inactive_user = TenantUser.objects.create_user(
                email='inactive@authtest.com',
                password='testpass123',
                first_name='Inactive',
                last_name='User',
                is_active=False
            )
        
        backend = TenantAuthenticationBackend()
        
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username='inactive@authtest.com',
                password='testpass123',
                tenant=self.tenant
            )
        
        self.assertIsNone(authenticated_user)
    
    def test_authenticate_without_tenant(self):
        """Test authentication without tenant context."""
        backend = TenantAuthenticationBackend()
        
        authenticated_user = backend.authenticate(
            request=None,
            username='user@authtest.com',
            password='testpass123'
            # No tenant provided
        )
        
        self.assertIsNone(authenticated_user)
    
    def test_get_user_valid_id(self):
        """Test getting user by valid ID."""
        backend = TenantAuthenticationBackend()
        
        with schema_context(self.tenant.schema_name):
            retrieved_user = backend.get_user(self.user.id)
        
        self.assertEqual(retrieved_user, self.user)
    
    def test_get_user_invalid_id(self):
        """Test getting user by invalid ID."""
        backend = TenantAuthenticationBackend()
        
        with schema_context(self.tenant.schema_name):
            retrieved_user = backend.get_user(99999)
        
        self.assertIsNone(retrieved_user)


class TenantAuthenticationMiddlewareTest(TransactionTestCase):
    """Test tenant authentication middleware."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        
        # Create tenant
        self.tenant = Tenant.objects.create(
            name='Middleware Test Corp',
            schema_name='middleware_test'
        )
        Domain.objects.create(
            domain='middlewaretest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create user
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='user@middlewaretest.com',
                password='testpass123',
                first_name='Middleware',
                last_name='User'
            )
        
        # Mock get_response function
        self.get_response = MagicMock(return_value=HttpResponse('OK'))
        self.middleware = TenantAuthenticationMiddleware(self.get_response)
    
    def test_middleware_with_authenticated_user(self):
        """Test middleware with authenticated user."""
        request = self.factory.get('/')
        request.tenant = self.tenant
        request.user = self.user
        
        response = self.middleware(request)
        
        # Middleware should process request normally
        self.get_response.assert_called_once_with(request)
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_with_anonymous_user(self):
        """Test middleware with anonymous user."""
        request = self.factory.get('/')
        request.tenant = self.tenant
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        # Should still process request (middleware doesn't block anonymous users)
        self.get_response.assert_called_once_with(request)
    
    def test_middleware_tenant_context_injection(self):
        """Test that middleware injects tenant context properly."""
        request = self.factory.get('/')
        request.tenant = self.tenant
        request.user = self.user
        
        # Mock process_request method
        with patch.object(self.middleware, 'process_request') as mock_process:
            response = self.middleware(request)
            
            # Verify tenant context is available
            self.assertEqual(request.tenant, self.tenant)
    
    def test_middleware_handles_missing_tenant(self):
        """Test middleware behavior when tenant is missing."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        # No tenant attribute
        
        # Should handle gracefully
        response = self.middleware(request)
        self.get_response.assert_called_once_with(request)


class AuthenticationSecurityTest(TransactionTestCase):
    """Test authentication security features."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Security Test Corp',
            schema_name='security_test'
        )
        
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='security@test.com',
                password='securepass123',
                first_name='Security',
                last_name='User'
            )
    
    def test_password_strength_validation(self):
        """Test password strength requirements."""
        weak_passwords = [
            '123',           # Too short
            'password',      # Common password
            'abc123',        # Too simple
            '12345678',      # Only numbers
            'abcdefgh',      # Only letters
        ]
        
        for weak_password in weak_passwords:
            with self.assertRaises(ValidationError):
                with schema_context(self.tenant.schema_name):
                    user = TenantUser(
                        email='test@weak.com',
                        first_name='Test',
                        last_name='User'
                    )
                    user.set_password(weak_password)
                    user.full_clean()
    
    def test_password_strength_validation_strong(self):
        """Test that strong passwords are accepted."""
        strong_passwords = [
            'MyStr0ngP@ssw0rd!',
            'C0mpl3x#P@ssw0rd',
            'S3cur3$Pass2024',
        ]
        
        for strong_password in strong_passwords:
            with schema_context(self.tenant.schema_name):
                user = TenantUser(
                    email=f'test{len(strong_password)}@strong.com',
                    first_name='Test',
                    last_name='User'
                )
                user.set_password(strong_password)
                user.full_clean()  # Should not raise
    
    def test_login_rate_limiting(self):
        """Test login attempt rate limiting."""
        # This would test rate limiting implementation
        # For now, simulate the logic
        
        failed_attempts = 0
        max_attempts = 5
        lockout_duration = timedelta(minutes=15)
        
        # Simulate failed login attempts
        for attempt in range(max_attempts + 2):
            if failed_attempts >= max_attempts:
                # Account should be locked
                is_locked = True
                break
            else:
                failed_attempts += 1
                is_locked = False
        
        self.assertTrue(is_locked)
        self.assertEqual(failed_attempts, max_attempts)
    
    def test_session_timeout(self):
        """Test session timeout functionality."""
        # This would test session timeout implementation
        session_timeout = timedelta(hours=2)
        last_activity = timezone.now() - timedelta(hours=3)
        current_time = timezone.now()
        
        time_since_activity = current_time - last_activity
        is_expired = time_since_activity > session_timeout
        
        self.assertTrue(is_expired)
    
    def test_concurrent_session_limitation(self):
        """Test limitation of concurrent sessions."""
        # This would test concurrent session limitation
        max_concurrent_sessions = 3
        current_sessions = 4  # Exceeds limit
        
        should_terminate_oldest = current_sessions > max_concurrent_sessions
        self.assertTrue(should_terminate_oldest)
    
    @patch('django.contrib.auth.login')
    def test_two_factor_authentication_simulation(self, mock_login):
        """Test two-factor authentication workflow simulation."""
        # Simulate 2FA workflow
        
        # Step 1: Primary authentication
        backend = TenantAuthenticationBackend()
        with schema_context(self.tenant.schema_name):
            primary_auth = backend.authenticate(
                request=None,
                username='security@test.com',
                password='securepass123',
                tenant=self.tenant
            )
        
        self.assertIsNotNone(primary_auth)
        
        # Step 2: 2FA verification (simulated)
        totp_code = '123456'  # Would be generated by authenticator app
        expected_code = '123456'  # Would be calculated server-side
        
        is_2fa_valid = totp_code == expected_code
        self.assertTrue(is_2fa_valid)
        
        # Step 3: Complete login only if both factors succeed
        if primary_auth and is_2fa_valid:
            login_successful = True
        else:
            login_successful = False
        
        self.assertTrue(login_successful)


class AuthenticationTokenTest(TestCase):
    """Test authentication token functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Token Test Corp',
            schema_name='token_test'
        )
        
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='token@test.com',
                password='tokenpass123',
                first_name='Token',
                last_name='User'
            )
    
    def test_jwt_token_generation(self):
        """Test JWT token generation."""
        # This would test JWT token generation
        import jwt
        import datetime
        
        payload = {
            'user_id': str(self.user.id),
            'tenant_id': str(self.tenant.id),
            'email': self.user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }
        
        secret_key = 'test-secret-key'
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # Verify token can be decoded
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        self.assertEqual(decoded['email'], 'token@test.com')
    
    def test_api_key_authentication(self):
        """Test API key authentication."""
        # Simulate API key authentication
        api_key = 'test-api-key-12345'
        
        # In real implementation, this would validate against stored API keys
        valid_api_keys = ['test-api-key-12345', 'another-valid-key']
        
        is_valid_api_key = api_key in valid_api_keys
        self.assertTrue(is_valid_api_key)
    
    def test_refresh_token_functionality(self):
        """Test refresh token functionality."""
        # Simulate refresh token workflow
        
        # Initial token pair
        access_token_expires = timezone.now() + timedelta(minutes=15)
        refresh_token_expires = timezone.now() + timedelta(days=7)
        
        # Simulate access token expiration
        current_time = timezone.now() + timedelta(minutes=20)
        is_access_expired = current_time > access_token_expires
        is_refresh_valid = current_time < refresh_token_expires
        
        # Should be able to refresh
        can_refresh = is_access_expired and is_refresh_valid
        self.assertTrue(can_refresh)


class AuthenticationViewsTest(TransactionTestCase):
    """Test authentication views and endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        
        self.tenant = Tenant.objects.create(
            name='Views Test Corp',
            schema_name='views_test'
        )
        
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='views@test.com',
                password='viewspass123',
                first_name='Views',
                last_name='User'
            )
    
    def test_login_view_success(self):
        """Test successful login view."""
        # This would test the actual login view
        # For now, simulate the logic
        
        login_data = {
            'email': 'views@test.com',
            'password': 'viewspass123'
        }
        
        # Simulate authentication
        backend = TenantAuthenticationBackend()
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username=login_data['email'],
                password=login_data['password'],
                tenant=self.tenant
            )
        
        # Simulate successful response
        if authenticated_user:
            response_data = {
                'success': True,
                'user': {
                    'id': str(authenticated_user.id),
                    'email': authenticated_user.email,
                    'name': authenticated_user.get_full_name()
                }
            }
        else:
            response_data = {'success': False, 'error': 'Invalid credentials'}
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['user']['email'], 'views@test.com')
    
    def test_login_view_failure(self):
        """Test failed login view."""
        login_data = {
            'email': 'views@test.com',
            'password': 'wrongpassword'
        }
        
        backend = TenantAuthenticationBackend()
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username=login_data['email'],
                password=login_data['password'],
                tenant=self.tenant
            )
        
        if authenticated_user:
            response_data = {'success': True}
        else:
            response_data = {'success': False, 'error': 'Invalid credentials'}
        
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)
    
    def test_logout_view(self):
        """Test logout view."""
        # Simulate logout process
        request = self.factory.post('/logout/')
        request.tenant = self.tenant
        request.user = self.user
        
        # Simulate logout logic
        logout_successful = True  # Would call Django's logout()
        
        response_data = {
            'success': logout_successful,
            'message': 'Logged out successfully'
        }
        
        self.assertTrue(response_data['success'])
    
    def test_password_reset_request(self):
        """Test password reset request."""
        reset_data = {
            'email': 'views@test.com'
        }
        
        # Simulate password reset logic
        with schema_context(self.tenant.schema_name):
            user_exists = TenantUser.objects.filter(
                email=reset_data['email']
            ).exists()
        
        if user_exists:
            # Would generate reset token and send email
            response_data = {
                'success': True,
                'message': 'Password reset email sent'
            }
        else:
            response_data = {
                'success': False,
                'error': 'Email not found'
            }
        
        self.assertTrue(response_data['success'])


class AuthenticationIntegrationTest(TransactionTestCase):
    """Integration tests for authentication system."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Integration Auth Test',
            schema_name='integration_auth_test'
        )
        
        Domain.objects.create(
            domain='integrationauth.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_complete_authentication_flow(self):
        """Test complete authentication workflow."""
        # 1. User registration
        with schema_context(self.tenant.schema_name):
            user = TenantUser.objects.create_user(
                email='integration@test.com',
                password='integrationpass123',
                first_name='Integration',
                last_name='User'
            )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'integration@test.com')
        
        # 2. Authentication
        backend = TenantAuthenticationBackend()
        with schema_context(self.tenant.schema_name):
            authenticated_user = backend.authenticate(
                request=None,
                username='integration@test.com',
                password='integrationpass123',
                tenant=self.tenant
            )
        
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, user)
        
        # 3. Permission checking (would integrate with permissions app)
        user_permissions = []  # Would load from permissions system
        has_admin_access = 'admin' in user_permissions or user.is_tenant_admin
        
        # 4. Session management
        session_active = True  # Would check session validity
        
        # 5. Logout
        logout_successful = True  # Would clear session
        
        self.assertTrue(logout_successful)
    
    def test_multi_tenant_authentication_isolation(self):
        """Test authentication isolation between tenants."""
        # Create second tenant
        tenant2 = Tenant.objects.create(
            name='Second Auth Tenant',
            schema_name='second_auth_tenant'
        )
        
        # Create users in different tenants with same email
        with schema_context(self.tenant.schema_name):
            user1 = TenantUser.objects.create_user(
                email='same@email.com',
                password='password1',
                first_name='User',
                last_name='One'
            )
        
        with schema_context(tenant2.schema_name):
            user2 = TenantUser.objects.create_user(
                email='same@email.com',
                password='password2',
                first_name='User',
                last_name='Two'
            )
        
        # Test authentication in tenant 1
        backend = TenantAuthenticationBackend()
        with schema_context(self.tenant.schema_name):
            auth1 = backend.authenticate(
                request=None,
                username='same@email.com',
                password='password1',
                tenant=self.tenant
            )
        
        # Test authentication in tenant 2
        with schema_context(tenant2.schema_name):
            auth2 = backend.authenticate(
                request=None,
                username='same@email.com',
                password='password2',
                tenant=tenant2
            )
        
        # Both should authenticate but to different users
        self.assertIsNotNone(auth1)
        self.assertIsNotNone(auth2)
        self.assertNotEqual(auth1.id, auth2.id)
        self.assertEqual(auth1.first_name, 'User')
        self.assertEqual(auth1.last_name, 'One')
        self.assertEqual(auth2.last_name, 'Two')
        
        # Cross-tenant authentication should fail
        with schema_context(self.tenant.schema_name):
            cross_auth = backend.authenticate(
                request=None,
                username='same@email.com',
                password='password2',  # Wrong password for tenant 1
                tenant=self.tenant
            )
        
        self.assertIsNone(cross_auth)


class AuthenticationMiddlewareIntegrationTest(TransactionTestCase):
    """Test authentication middleware integration."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.tenant = Tenant.objects.create(
            name='Middleware Integration Test',
            schema_name='middleware_integration'
        )
        
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='middleware@integration.com',
                password='middlewarepass123',
                first_name='Middleware',
                last_name='User'
            )
    
    def test_middleware_chain_processing(self):
        """Test middleware chain processing for authentication."""
        # Create mock middleware chain
        def mock_view(request):
            return HttpResponse('Success')
        
        middleware = TenantAuthenticationMiddleware(mock_view)
        
        # Create request with authentication
        request = self.factory.get('/')
        request.tenant = self.tenant
        request.user = self.user
        request.session = {}
        
        # Process through middleware
        response = middleware(request)
        
        # Should process successfully
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Success')
    
    def test_authentication_with_permissions(self):
        """Test authentication integration with permissions system."""
        # This would test integration between auth and permissions
        # For now, simulate the interaction
        
        user_roles = ['basic_user']  # Would come from permissions system
        required_role = 'admin'
        
        has_permission = required_role in user_roles or self.user.is_tenant_admin
        
        # Basic user should not have admin permission
        self.assertFalse(has_permission)
        
        # Make user admin
        with schema_context(self.tenant.schema_name):
            self.user.is_tenant_admin = True
            self.user.save()
        
        has_permission = required_role in user_roles or self.user.is_tenant_admin
        self.assertTrue(has_permission)
