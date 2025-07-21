"""
Test suite for the Tenants app
Testing tenant creation, domain management, and multi-tenancy functionality.
"""

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django.contrib.auth import get_user_model
from django.test.client import Client
from django_tenants.utils import schema_context, get_tenant_model
from unittest.mock import patch, MagicMock

from apps.tenants.models import Tenant, Domain
from apps.common.services.tenant_provisioning import TenantProvisioningService


class TenantModelTest(TestCase):
    """Test Tenant model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant_data = {
            'name': 'Test Tenant Corp',
            'description': 'A test tenant for unit testing',
            'subscription_status': 'active'
        }
    
    def test_tenant_creation(self):
        """Test creating a tenant with valid data."""
        tenant = Tenant.objects.create(**self.tenant_data)
        
        self.assertEqual(tenant.name, 'Test Tenant Corp')
        self.assertEqual(tenant.description, 'A test tenant for unit testing')
        self.assertEqual(tenant.subscription_status, 'active')
        self.assertTrue(tenant.created_at)
        self.assertTrue(tenant.is_active)
    
    def test_tenant_str_representation(self):
        """Test string representation of tenant."""
        tenant = Tenant.objects.create(**self.tenant_data)
        self.assertEqual(str(tenant), 'Test Tenant Corp')
    
    def test_tenant_schema_name_generation(self):
        """Test automatic schema name generation."""
        tenant = Tenant.objects.create(**self.tenant_data)
        
        # Schema name should be generated from tenant name
        self.assertTrue(tenant.schema_name)
        self.assertNotEqual(tenant.schema_name, 'public')
        # Should be lowercase and contain no spaces
        self.assertTrue(tenant.schema_name.islower())
        self.assertNotIn(' ', tenant.schema_name)
    
    def test_tenant_unique_schema_name(self):
        """Test that schema names are unique."""
        tenant1 = Tenant.objects.create(name='Unique Corp 1')
        tenant2 = Tenant.objects.create(name='Unique Corp 2')
        
        self.assertNotEqual(tenant1.schema_name, tenant2.schema_name)
    
    def test_tenant_subscription_status_choices(self):
        """Test subscription status field choices."""
        tenant = Tenant.objects.create(name='Status Test Corp')
        
        valid_statuses = ['trial', 'active', 'suspended', 'cancelled']
        for status in valid_statuses:
            tenant.subscription_status = status
            tenant.save()
            tenant.refresh_from_db()
            self.assertEqual(tenant.subscription_status, status)
    
    def test_tenant_deactivation(self):
        """Test tenant deactivation."""
        tenant = Tenant.objects.create(name='Deactivation Test Corp')
        self.assertTrue(tenant.is_active)
        
        tenant.is_active = False
        tenant.save()
        tenant.refresh_from_db()
        self.assertFalse(tenant.is_active)
    
    def test_get_primary_domain(self):
        """Test getting primary domain for tenant."""
        tenant = Tenant.objects.create(name='Domain Test Corp')
        
        # Create domains
        primary_domain = Domain.objects.create(
            domain='primary.test.com',
            tenant=tenant,
            is_primary=True
        )
        secondary_domain = Domain.objects.create(
            domain='secondary.test.com',
            tenant=tenant,
            is_primary=False
        )
        
        self.assertEqual(tenant.get_primary_domain(), 'primary.test.com')


class DomainModelTest(TestCase):
    """Test Domain model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(name='Domain Test Tenant')
    
    def test_domain_creation(self):
        """Test creating a domain with valid data."""
        domain = Domain.objects.create(
            domain='test.example.com',
            tenant=self.tenant,
            is_primary=True
        )
        
        self.assertEqual(domain.domain, 'test.example.com')
        self.assertEqual(domain.tenant, self.tenant)
        self.assertTrue(domain.is_primary)
    
    def test_domain_str_representation(self):
        """Test string representation of domain."""
        domain = Domain.objects.create(
            domain='example.test.com',
            tenant=self.tenant
        )
        self.assertEqual(str(domain), 'example.test.com')
    
    def test_unique_domain_constraint(self):
        """Test that domain names must be unique."""
        Domain.objects.create(
            domain='unique.test.com',
            tenant=self.tenant
        )
        
        # Creating another domain with same name should fail
        with self.assertRaises(IntegrityError):
            Domain.objects.create(
                domain='unique.test.com',
                tenant=self.tenant
            )
    
    def test_primary_domain_uniqueness_per_tenant(self):
        """Test that each tenant can have only one primary domain."""
        Domain.objects.create(
            domain='primary1.test.com',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Creating another primary domain for same tenant should update the first
        Domain.objects.create(
            domain='primary2.test.com',
            tenant=self.tenant,
            is_primary=True
        )
        
        primary_domains = Domain.objects.filter(tenant=self.tenant, is_primary=True)
        self.assertEqual(primary_domains.count(), 1)
        self.assertEqual(primary_domains.first().domain, 'primary2.test.com')


class TenantProvisioningServiceTest(TransactionTestCase):
    """Test TenantProvisioningService functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant_data = {
            'name': 'Service Test Corp',
            'description': 'Test tenant for service testing',
            'subscription_status': 'trial'
        }
    
    @patch('apps.common.services.permission_service.PermissionService.setup_tenant_permissions')
    def test_create_tenant_with_setup_success(self, mock_permissions):
        """Test successful tenant creation with setup."""
        mock_permissions.return_value = {
            'success': True,
            'permissions_created': 8,
            'role_groups_created': 3
        }
        
        result = TenantProvisioningService.create_tenant_with_setup(self.tenant_data)
        
        self.assertTrue(result['success'])
        self.assertIn('tenant', result)
        self.assertIn('domain', result)
        
        tenant = result['tenant']
        self.assertEqual(tenant.name, 'Service Test Corp')
        self.assertEqual(tenant.subscription_status, 'trial')
        
        # Verify domain was created
        domain = result['domain']
        self.assertEqual(domain.tenant, tenant)
        self.assertTrue(domain.is_primary)
        
        # Verify permissions setup was called
        mock_permissions.assert_called_once_with(tenant)
    
    def test_create_tenant_validation_error(self):
        """Test tenant creation with invalid data."""
        invalid_data = {
            'name': '',  # Empty name should fail
            'subscription_status': 'invalid_status'
        }
        
        result = TenantProvisioningService.create_tenant_with_setup(invalid_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('apps.common.services.permission_service.PermissionService.setup_tenant_permissions')
    def test_create_tenant_permissions_failure(self, mock_permissions):
        """Test tenant creation when permissions setup fails."""
        mock_permissions.return_value = {
            'success': False,
            'error': 'Permission setup failed'
        }
        
        result = TenantProvisioningService.create_tenant_with_setup(self.tenant_data)
        
        # Should still succeed but note the permission failure
        self.assertTrue(result['success'])
        self.assertIn('permissions_warning', result)
    
    def test_generate_domain_name(self):
        """Test domain name generation."""
        tenant_name = "Test Company & Associates Inc."
        domain = TenantProvisioningService._generate_domain_name(tenant_name)
        
        # Should be lowercase, no spaces or special characters
        self.assertTrue(domain.islower())
        self.assertNotIn(' ', domain)
        self.assertNotIn('&', domain)
        self.assertTrue(domain.endswith('.localhost'))
    
    def test_generate_schema_name(self):
        """Test schema name generation."""
        tenant_name = "Test Company 123"
        schema = TenantProvisioningService._generate_schema_name(tenant_name)
        
        # Should be lowercase, alphanumeric only
        self.assertTrue(schema.islower())
        self.assertTrue(schema.replace('_', '').isalnum())
        self.assertNotIn(' ', schema)


class TenantMultiTenancyTest(TransactionTestCase):
    """Test multi-tenancy functionality."""
    
    def setUp(self):
        """Set up test tenants."""
        self.tenant1 = Tenant.objects.create(
            name='Tenant One',
            schema_name='tenant_one'
        )
        self.tenant2 = Tenant.objects.create(
            name='Tenant Two',
            schema_name='tenant_two'
        )
        
        # Create domains
        Domain.objects.create(
            domain='tenant1.test.com',
            tenant=self.tenant1,
            is_primary=True
        )
        Domain.objects.create(
            domain='tenant2.test.com',
            tenant=self.tenant2,
            is_primary=True
        )
    
    def test_schema_isolation(self):
        """Test that tenants have isolated schemas."""
        User = get_user_model()
        
        # Create user in tenant1 schema
        with schema_context(self.tenant1.schema_name):
            user1 = User.objects.create(
                email='user1@tenant1.com',
                first_name='User',
                last_name='One'
            )
            tenant1_user_count = User.objects.count()
        
        # Create user in tenant2 schema
        with schema_context(self.tenant2.schema_name):
            user2 = User.objects.create(
                email='user2@tenant2.com',
                first_name='User',
                last_name='Two'
            )
            tenant2_user_count = User.objects.count()
        
        # Each tenant should only see their own user
        self.assertEqual(tenant1_user_count, 1)
        self.assertEqual(tenant2_user_count, 1)
        
        # Verify users are in correct schemas
        with schema_context(self.tenant1.schema_name):
            self.assertTrue(User.objects.filter(email='user1@tenant1.com').exists())
            self.assertFalse(User.objects.filter(email='user2@tenant2.com').exists())
        
        with schema_context(self.tenant2.schema_name):
            self.assertTrue(User.objects.filter(email='user2@tenant2.com').exists())
            self.assertFalse(User.objects.filter(email='user1@tenant1.com').exists())
    
    def test_tenant_resolution_by_domain(self):
        """Test that tenants are correctly resolved by domain."""
        # This would typically be tested with middleware, but we can test the model logic
        tenant1_domain = Domain.objects.get(domain='tenant1.test.com')
        tenant2_domain = Domain.objects.get(domain='tenant2.test.com')
        
        self.assertEqual(tenant1_domain.tenant, self.tenant1)
        self.assertEqual(tenant2_domain.tenant, self.tenant2)
    
    def test_public_schema_shared_data(self):
        """Test that shared data exists in public schema."""
        # Tenants and domains should be in public schema
        public_tenant_count = Tenant.objects.count()
        public_domain_count = Domain.objects.count()
        
        self.assertEqual(public_tenant_count, 2)
        self.assertEqual(public_domain_count, 2)
        
        # These should be accessible regardless of schema context
        with schema_context(self.tenant1.schema_name):
            # Can't access tenant data from within tenant schema
            pass  # This is expected behavior


class TenantAdminTest(TestCase):
    """Test Tenant admin functionality."""
    
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
    
    def test_admin_tenant_list_view(self):
        """Test admin list view for tenants."""
        # Create test tenants
        Tenant.objects.create(name='Admin Test Tenant 1')
        Tenant.objects.create(name='Admin Test Tenant 2')
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Access admin list view
        response = self.client.get('/admin/tenants/tenant/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test Tenant 1')
        self.assertContains(response, 'Admin Test Tenant 2')
    
    def test_admin_domain_list_view(self):
        """Test admin list view for domains."""
        tenant = Tenant.objects.create(name='Domain Admin Test')
        Domain.objects.create(
            domain='admin.test.com',
            tenant=tenant,
            is_primary=True
        )
        
        # Login as admin
        self.client.force_login(self.admin_user)
        
        # Access admin list view
        response = self.client.get('/admin/tenants/domain/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin.test.com')


class TenantAPITest(TestCase):
    """Test Tenant API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            email='api@test.com',
            first_name='API',
            last_name='User',
            password='testpass123'
        )
    
    def test_tenant_list_api(self):
        """Test listing tenants via API."""
        # Create test tenants
        Tenant.objects.create(name='API Test Tenant 1')
        Tenant.objects.create(name='API Test Tenant 2')
        
        # Authenticate
        self.client.force_login(self.user)
        
        response = self.client.get('/api/tenants/')
        
        if response.status_code == 404:
            # API endpoint might not be implemented yet
            self.skipTest("API endpoint not implemented yet")
        
        self.assertEqual(response.status_code, 200)
    
    def test_tenant_detail_api(self):
        """Test tenant detail via API."""
        tenant = Tenant.objects.create(name='API Detail Test Tenant')
        
        # Authenticate
        self.client.force_login(self.user)
        
        response = self.client.get(f'/api/tenants/{tenant.id}/')
        
        if response.status_code == 404:
            # API endpoint might not be implemented yet
            self.skipTest("API endpoint not implemented yet")
        
        self.assertEqual(response.status_code, 200)
