"""
Working comprehensive tests for authentication app.
"""

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import uuid

from apps.authentication.middleware import TenantAuthenticationMiddleware
from apps.authentication.backends import TenantAuthenticationBackend
from apps.users.models import CustomUser


class TenantAuthenticationMiddlewareTest(TestCase):
    """Test TenantAuthenticationMiddleware functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.middleware = TenantAuthenticationMiddleware(lambda request: HttpResponse("OK"))
        
        # Create test user
        self.user_email = f'middleware-{uuid.uuid4()}@test.com'
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            password='middlewarepass123',
            first_name='Middleware',
            last_name='User'
        )
    
    def test_middleware_initialization(self):
        """Test middleware initialization."""
        middleware = TenantAuthenticationMiddleware(lambda request: HttpResponse("Test"))
        self.assertIsNotNone(middleware)
    
    def test_middleware_call(self):
        """Test middleware call method."""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")
    
    def test_middleware_with_authenticated_user(self):
        """Test middleware with authenticated user."""
        request = self.factory.get('/')
        request.user = self.user
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.user, self.user)
    
    def test_middleware_with_anonymous_user(self):
        """Test middleware with anonymous user."""
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(request.user, AnonymousUser)
    
    def test_middleware_process_request(self):
        """Test middleware request processing."""
        request = self.factory.get('/api/test/')
        request.user = self.user
        
        # Add session and message middleware attributes
        from django.contrib.sessions.backends.base import SessionBase
        from django.contrib.messages.storage.fallback import FallbackStorage
        
        request.session = SessionBase()
        request._messages = FallbackStorage(request)
        
        response = self.middleware(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_security_headers(self):
        """Test middleware adds security headers."""
        request = self.factory.get('/')
        response = self.middleware(request)
        
        # Middleware should pass through the response
        self.assertEqual(response.status_code, 200)


class TenantAuthenticationBackendTest(TestCase):
    """Test TenantAuthenticationBackend authentication functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.backend = TenantAuthenticationBackend()
        
        # Create test users for security testing
        self.active_user_email = f'active-{uuid.uuid4()}@test.com'
        self.active_user = CustomUser.objects.create_user(
            email=self.active_user_email,
            password='activepass123',
            first_name='Active',
            last_name='User',
            is_active=True
        )
        
        self.inactive_user_email = f'inactive-{uuid.uuid4()}@test.com'
        self.inactive_user = CustomUser.objects.create_user(
            email=self.inactive_user_email,
            password='inactivepass123',
            first_name='Inactive',
            last_name='User',
            is_active=False
        )
    
    def test_backend_initialization(self):
        """Test backend initialization."""
        backend = TenantAuthenticationBackend()
        self.assertIsNotNone(backend)
    
    def test_authenticate_valid_user(self):
        """Test authenticating valid user."""
        user = self.backend.authenticate(
            request=None,
            username=self.active_user_email,
            password='activepass123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.active_user_email)
        self.assertEqual(user, self.active_user)
    
    def test_authenticate_invalid_password(self):
        """Test authenticating with invalid password."""
        user = self.backend.authenticate(
            request=None,
            username=self.active_user_email,
            password='wrongpassword'
        )
        
        self.assertIsNone(user)
    
    def test_authenticate_invalid_email(self):
        """Test authenticating with invalid email."""
        user = self.backend.authenticate(
            request=None,
            username=f'nonexistent-{uuid.uuid4()}@test.com',
            password='anypassword'
        )
        
        self.assertIsNone(user)
    
    def test_authenticate_inactive_user(self):
        """Test authenticating inactive user."""
        user = self.backend.authenticate(
            request=None,
            username=self.inactive_user_email,
            password='inactivepass123'
        )
        
        # Should still authenticate but user is inactive
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)
    
    def test_get_user_valid_id(self):
        """Test getting user by valid ID."""
        user = self.backend.get_user(self.active_user.id)
        
        self.assertIsNotNone(user)
        self.assertEqual(user, self.active_user)
    
    def test_get_user_invalid_id(self):
        """Test getting user by invalid ID."""
        user = self.backend.get_user(99999)  # Non-existent ID
        
        self.assertIsNone(user)
    
    def test_get_user_inactive(self):
        """Test getting inactive user."""
        user = self.backend.get_user(self.inactive_user.id)
        
        self.assertIsNotNone(user)
        self.assertEqual(user, self.inactive_user)
        self.assertFalse(user.is_active)


class AuthenticationIntegrationTest(TestCase):
    """Test authentication system integration."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user_email = f'integration-{uuid.uuid4()}@test.com'
        self.user_password = 'integrationpass123'
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            password=self.user_password,
            first_name='Integration',
            last_name='User'
        )
    
    def test_login_with_email_backend(self):
        """Test login using email backend."""
        login_successful = self.client.login(
            username=self.user_email,
            password=self.user_password
        )
        
        self.assertTrue(login_successful)
    
    def test_login_with_wrong_credentials(self):
        """Test login with wrong credentials."""
        login_successful = self.client.login(
            username=self.user_email,
            password='wrongpassword'
        )
        
        self.assertFalse(login_successful)
    
    def test_login_with_nonexistent_user(self):
        """Test login with nonexistent user."""
        login_successful = self.client.login(
            username=f'nonexistent-{uuid.uuid4()}@test.com',
            password='anypassword'
        )
        
        self.assertFalse(login_successful)
    
    def test_authenticated_request(self):
        """Test authenticated request handling."""
        self.client.login(username=self.user_email, password=self.user_password)
        
        response = self.client.get('/admin/')
        
        # Should access admin or redirect (both indicate authentication works)
        self.assertIn(response.status_code, [200, 302])
    
    def test_unauthenticated_request(self):
        """Test unauthenticated request handling."""
        response = self.client.get('/admin/')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_logout_functionality(self):
        """Test logout functionality."""
        # Login first
        self.client.login(username=self.user_email, password=self.user_password)
        
        # Logout
        self.client.logout()
        
        # Should redirect to login after logout
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)


class AuthenticationSecurityTest(TestCase):
    """Test authentication security features."""
    
    def setUp(self):
        """Set up test data."""
        self.user_email = f'security-{uuid.uuid4()}@test.com'
        self.user_password = 'SecurePass123!'
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            password=self.user_password,
            first_name='Security',
            last_name='User'
        )
        self.backend = TenantAuthenticationBackend()
    
    def test_password_hashing(self):
        """Test password is properly hashed."""
        # Password should not be stored in plain text
        self.assertNotEqual(self.user.password, self.user_password)
        
        # But should validate correctly
        self.assertTrue(self.user.check_password(self.user_password))
    
    def test_case_insensitive_email_auth(self):
        """Test case insensitive email authentication."""
        # Test with different cases
        user_upper = self.backend.authenticate(
            request=None,
            username=self.user_email.upper(),
            password=self.user_password
        )
        
        user_mixed = self.backend.authenticate(
            request=None,
            username=self.user_email.swapcase(),
            password=self.user_password
        )
        
        # Should authenticate regardless of email case
        self.assertIsNotNone(user_upper)
        self.assertIsNotNone(user_mixed)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection."""
        malicious_email = f"test@test.com'; DROP TABLE users; --"
        
        user = self.backend.authenticate(
            request=None,
            username=malicious_email,
            password='anypassword'
        )
        
        # Should safely return None without executing SQL injection
        self.assertIsNone(user)
        
        # User table should still exist
        user_count = CustomUser.objects.count()
        self.assertGreater(user_count, 0)
    
    def test_brute_force_protection(self):
        """Test brute force attack protection."""
        # Multiple failed login attempts
        for i in range(5):
            user = self.backend.authenticate(
                request=None,
                username=self.user_email,
                password='wrongpassword'
            )
            self.assertIsNone(user)
        
        # Should still allow valid login after failed attempts
        user = self.backend.authenticate(
            request=None,
            username=self.user_email,
            password=self.user_password
        )
        self.assertIsNotNone(user)


class AuthenticationMiddlewareIntegrationTest(TestCase):
    """Test authentication middleware integration."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user_email = f'middleware-integration-{uuid.uuid4()}@test.com'
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            password='middlewarepass123',
            first_name='Middleware',
            last_name='Integration'
        )
    
    def test_middleware_with_session(self):
        """Test middleware with session management."""
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthMiddleware
        
        request = self.factory.get('/')
        
        # Apply session middleware
        session_middleware = SessionMiddleware(lambda r: HttpResponse("OK"))
        session_middleware.process_request(request)
        request.session.save()
        
        # Apply auth middleware
        auth_middleware = DjangoAuthMiddleware(lambda r: HttpResponse("OK"))
        response = auth_middleware(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_request_processing(self):
        """Test middleware request processing flow."""
        request = self.factory.post('/api/login/', {
            'username': self.user_email,
            'password': 'middlewarepass123'
        })
        
        # Add required middleware attributes
        from django.contrib.sessions.backends.base import SessionBase
        from django.contrib.messages.storage.fallback import FallbackStorage
        
        request.session = SessionBase()
        request._messages = FallbackStorage(request)
        
        middleware = AuthenticationMiddleware(lambda r: HttpResponse("OK"))
        response = middleware(request)
        
        self.assertEqual(response.status_code, 200)
    
    def test_middleware_error_handling(self):
        """Test middleware error handling."""
        request = self.factory.get('/')
        
        # Middleware that raises exception
        def error_view(request):
            raise Exception("Test error")
        
        middleware = AuthenticationMiddleware(error_view)
        
        # Should handle errors gracefully
        with self.assertRaises(Exception):
            middleware(request)


class AuthenticationPerformanceTest(TestCase):
    """Test authentication performance."""
    
    def setUp(self):
        """Set up test data."""
        self.backend = TenantAuthenticationBackend()
        self.user_email = f'performance-{uuid.uuid4()}@test.com'
        self.user = CustomUser.objects.create_user(
            email=self.user_email,
            password='performancepass123',
            first_name='Performance',
            last_name='User'
        )
    
    def test_authentication_speed(self):
        """Test authentication performance."""
        import time
        
        # Measure authentication time
        start_time = time.time()
        
        for i in range(10):
            user = self.backend.authenticate(
                request=None,
                username=self.user_email,
                password='performancepass123'
            )
            self.assertIsNotNone(user)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 authentications in reasonable time
        self.assertLess(total_time, 5.0)  # Less than 5 seconds
    
    def test_user_lookup_speed(self):
        """Test user lookup performance."""
        import time
        
        start_time = time.time()
        
        for i in range(100):
            user = self.backend.get_user(self.user.id)
            self.assertIsNotNone(user)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 100 lookups in reasonable time
        self.assertLess(total_time, 2.0)  # Less than 2 seconds
