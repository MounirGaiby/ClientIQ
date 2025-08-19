"""
Comprehensive tests for tenants app.
Tests Tenant model, Domain model, and tenant management functionality.
"""

from django.test import TestCase, TransactionTestCase
from django.db import IntegrityError, connection
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from django_tenants.utils import schema_context, tenant_context
from django_tenants.test.cases import TenantTestCase

from apps.tenants.models import Tenant, Domain
from apps.tenants.admin import TenantAdmin, DomainAdmin


class TenantModelTest(TestCase):
    """Test Tenant model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant_data = {
            'schema_name': 'testcorp',
            'name': 'Test Corporation',
            'contact_email': 'admin@testcorp.com',
            'description': 'A test corporation for testing purposes.'
        }
    
    def test_create_tenant(self):
        """Test creating a tenant."""
        tenant = Tenant.objects.create(**self.tenant_data)
        
        self.assertEqual(tenant.schema_name, 'testcorp')
        self.assertEqual(tenant.name, 'Test Corporation')
        self.assertEqual(tenant.contact_email, 'admin@testcorp.com')
        self.assertTrue(tenant.is_active)
        self.assertIsNotNone(tenant.created_at)
        self.assertIsNotNone(tenant.updated_at)
    
    def test_tenant_str_representation(self):
        """Test string representation of Tenant."""
        tenant = Tenant.objects.create(**self.tenant_data)
        expected = f"{tenant.name} ({tenant.schema_name})"
        self.assertEqual(str(tenant), expected)
    
    def test_schema_name_unique(self):
        """Test that schema_name must be unique."""
        Tenant.objects.create(**self.tenant_data)
        
        with self.assertRaises(IntegrityError):
            Tenant.objects.create(**self.tenant_data)
    
    def test_schema_name_validation(self):
        """Test schema_name validation."""
        # Test valid schema names
        valid_names = ['testcorp', 'test_corp', 'testcorp123']
        for name in valid_names:
            tenant = Tenant(schema_name=name, name='Test', contact_email='test@test.com')
            try:
                tenant.full_clean()
            except ValidationError:
                self.fail(f"Valid schema name '{name}' failed validation")
    
    def test_contact_email_validation(self):
        """Test contact_email validation."""
        tenant_data = self.tenant_data.copy()
        tenant_data['contact_email'] = 'invalid-email'
        
        tenant = Tenant(**tenant_data)
        with self.assertRaises(ValidationError):
            tenant.full_clean()
    
    def test_tenant_auto_create_schema(self):
        """Test that tenant schema is automatically created."""
        # Note: This test would require actual database schema creation
        # which is complex in test environment. We'll test the model creation only.
        tenant = Tenant.objects.create(**self.tenant_data)
        self.assertTrue(tenant.auto_create_schema)
    
    def test_tenant_auto_drop_schema(self):
        """Test tenant auto_drop_schema setting."""
        tenant = Tenant.objects.create(**self.tenant_data)
        self.assertTrue(tenant.auto_drop_schema)
    
    def test_tenant_deactivation(self):
        """Test tenant deactivation."""
        tenant = Tenant.objects.create(**self.tenant_data)
        self.assertTrue(tenant.is_active)
        
        tenant.is_active = False
        tenant.save()
        
        self.assertFalse(tenant.is_active)
    
    def test_tenant_ordering(self):
        """Test tenant default ordering."""
        # Create multiple tenants
        tenant1 = Tenant.objects.create(
            schema_name='tenant1',
            name='Tenant 1',
            contact_email='admin@tenant1.com'
        )
        tenant2 = Tenant.objects.create(
            schema_name='tenant2',
            name='Tenant 2', 
            contact_email='admin@tenant2.com'
        )
        
        # Test that they're ordered by name
        tenants = list(Tenant.objects.all())
        self.assertEqual(tenants[0].name, 'Tenant 1')
        self.assertEqual(tenants[1].name, 'Tenant 2')


class DomainModelTest(TestCase):
    """Test Domain model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            schema_name='testcorp',
            name='Test Corporation',
            contact_email='admin@testcorp.com'
        )
        
        self.domain_data = {
            'domain': 'testcorp.localhost',
            'tenant': self.tenant,
            'is_primary': True
        }
    
    def test_create_domain(self):
        """Test creating a domain."""
        domain = Domain.objects.create(**self.domain_data)
        
        self.assertEqual(domain.domain, 'testcorp.localhost')
        self.assertEqual(domain.tenant, self.tenant)
        self.assertTrue(domain.is_primary)
    
    def test_domain_str_representation(self):
        """Test string representation of Domain."""
        domain = Domain.objects.create(**self.domain_data)
        self.assertEqual(str(domain), 'testcorp.localhost')
    
    def test_domain_unique(self):
        """Test that domain must be unique."""
        Domain.objects.create(**self.domain_data)
        
        # Create another tenant
        tenant2 = Tenant.objects.create(
            schema_name='othercorp',
            name='Other Corporation',
            contact_email='admin@othercorp.com'
        )
        
        with self.assertRaises(IntegrityError):
            Domain.objects.create(
                domain='testcorp.localhost',
                tenant=tenant2,
                is_primary=True
            )
    
    def test_primary_domain_constraint(self):
        """Test that only one primary domain per tenant is allowed."""
        # Create first primary domain
        Domain.objects.create(**self.domain_data)
        
        # Try to create another primary domain for same tenant
        with self.assertRaises(IntegrityError):
            Domain.objects.create(
                domain='testcorp2.localhost',
                tenant=self.tenant,
                is_primary=True
            )
    
    def test_multiple_non_primary_domains(self):
        """Test that multiple non-primary domains are allowed."""
        # Create primary domain
        Domain.objects.create(**self.domain_data)
        
        # Create non-primary domains
        domain2 = Domain.objects.create(
            domain='testcorp2.localhost',
            tenant=self.tenant,
            is_primary=False
        )
        domain3 = Domain.objects.create(
            domain='testcorp3.localhost',
            tenant=self.tenant,
            is_primary=False
        )
        
        self.assertFalse(domain2.is_primary)
        self.assertFalse(domain3.is_primary)
    
    def test_domain_validation(self):
        """Test domain validation."""
        # Test valid domains
        valid_domains = [
            'example.com',
            'sub.example.com',
            'localhost',
            'test.localhost',
            '127.0.0.1',
            'example-site.com'
        ]
        
        for domain_name in valid_domains:
            domain = Domain(domain=domain_name, tenant=self.tenant, is_primary=False)
            try:
                domain.full_clean()
            except ValidationError:
                self.fail(f"Valid domain '{domain_name}' failed validation")
    
    def test_tenant_domains_relationship(self):
        """Test tenant-domains relationship."""
        # Create multiple domains for tenant
        domain1 = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        domain2 = Domain.objects.create(
            domain='testcorp.com',
            tenant=self.tenant,
            is_primary=False
        )
        
        # Test reverse relationship
        tenant_domains = self.tenant.domains.all()
        self.assertIn(domain1, tenant_domains)
        self.assertIn(domain2, tenant_domains)
        self.assertEqual(tenant_domains.count(), 2)
    
    def test_get_primary_domain(self):
        """Test getting primary domain for tenant."""
        primary_domain = Domain.objects.create(**self.domain_data)
        Domain.objects.create(
            domain='testcorp.com',
            tenant=self.tenant,
            is_primary=False
        )
        
        # Get primary domain
        tenant_primary = self.tenant.domains.filter(is_primary=True).first()
        self.assertEqual(tenant_primary, primary_domain)


class TenantAdminTest(TestCase):
    """Test Tenant admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_site = AdminSite()
        self.admin = TenantAdmin(Tenant, self.admin_site)
        
        self.tenant = Tenant.objects.create(
            schema_name='testcorp',
            name='Test Corporation',
            contact_email='admin@testcorp.com'
        )
    
    def test_admin_list_display(self):
        """Test admin list display configuration."""
        expected_fields = [
            'name', 'schema_name', 'contact_email',
            'is_active', 'created_at'
        ]
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test admin list filter configuration."""
        expected_filters = ['is_active', 'created_at']
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_admin_search_fields(self):
        """Test admin search fields configuration."""
        expected_fields = ['name', 'schema_name', 'contact_email']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_admin_readonly_fields(self):
        """Test admin readonly fields configuration."""
        readonly_fields = self.admin.readonly_fields
        self.assertIn('created_at', readonly_fields)
        self.assertIn('updated_at', readonly_fields)


class DomainAdminTest(TestCase):
    """Test Domain admin functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_site = AdminSite()
        self.admin = DomainAdmin(Domain, self.admin_site)
        
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
    
    def test_admin_list_display(self):
        """Test admin list display configuration."""
        expected_fields = ['domain', 'tenant', 'is_primary']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_admin_list_filter(self):
        """Test admin list filter configuration."""
        expected_filters = ['is_primary', 'tenant']
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_admin_search_fields(self):
        """Test admin search fields configuration."""
        expected_fields = ['domain', 'tenant__name', 'tenant__schema_name']
        self.assertEqual(list(self.admin.search_fields), expected_fields)


class TenantIntegrationTest(TransactionTestCase):
    """Integration tests for tenant functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant_data = {
            'schema_name': 'testcorp',
            'name': 'Test Corporation',
            'contact_email': 'admin@testcorp.com'
        }
    
    def test_tenant_with_domain_creation(self):
        """Test creating tenant with domain."""
        # Create tenant
        tenant = Tenant.objects.create(**self.tenant_data)
        
        # Create domain
        domain = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=tenant,
            is_primary=True
        )
        
        # Test relationship
        self.assertEqual(domain.tenant, tenant)
        self.assertIn(domain, tenant.domains.all())
    
    def test_tenant_cascade_delete(self):
        """Test that deleting tenant cascades to domains."""
        # Create tenant with domain
        tenant = Tenant.objects.create(**self.tenant_data)
        domain = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=tenant,
            is_primary=True
        )
        
        # Delete tenant
        tenant_id = tenant.id
        domain_id = domain.id
        tenant.delete()
        
        # Check that domain was also deleted
        self.assertFalse(Tenant.objects.filter(id=tenant_id).exists())
        self.assertFalse(Domain.objects.filter(id=domain_id).exists())
    
    def test_multiple_tenants_with_domains(self):
        """Test multiple tenants with their own domains."""
        # Create first tenant
        tenant1 = Tenant.objects.create(
            schema_name='tenant1',
            name='Tenant 1',
            contact_email='admin@tenant1.com'
        )
        domain1 = Domain.objects.create(
            domain='tenant1.localhost',
            tenant=tenant1,
            is_primary=True
        )
        
        # Create second tenant
        tenant2 = Tenant.objects.create(
            schema_name='tenant2',
            name='Tenant 2',
            contact_email='admin@tenant2.com'
        )
        domain2 = Domain.objects.create(
            domain='tenant2.localhost',
            tenant=tenant2,
            is_primary=True
        )
        
        # Test isolation
        self.assertEqual(tenant1.domains.count(), 1)
        self.assertEqual(tenant2.domains.count(), 1)
        self.assertEqual(tenant1.domains.first(), domain1)
        self.assertEqual(tenant2.domains.first(), domain2)
    
    def test_tenant_deactivation_workflow(self):
        """Test tenant deactivation workflow."""
        tenant = Tenant.objects.create(**self.tenant_data)
        domain = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=tenant,
            is_primary=True
        )
        
        # Deactivate tenant
        tenant.is_active = False
        tenant.save()
        
        # Tenant should be deactivated but domains should remain
        self.assertFalse(tenant.is_active)
        self.assertTrue(Domain.objects.filter(tenant=tenant).exists())
    
    def test_tenant_schema_name_constraints(self):
        """Test schema name constraints and validation."""
        # Test reserved schema names
        reserved_names = ['public', 'information_schema', 'pg_catalog', 'pg_toast']
        
        for reserved_name in reserved_names:
            with self.assertRaises((ValidationError, IntegrityError)):
                tenant = Tenant(
                    schema_name=reserved_name,
                    name='Test',
                    contact_email='test@test.com'
                )
                tenant.full_clean()
                tenant.save()
    
    def test_domain_routing_logic(self):
        """Test domain routing logic."""
        tenant = Tenant.objects.create(**self.tenant_data)
        
        # Create primary domain
        primary_domain = Domain.objects.create(
            domain='testcorp.localhost',
            tenant=tenant,
            is_primary=True
        )
        
        # Create alias domain
        alias_domain = Domain.objects.create(
            domain='testcorp.com',
            tenant=tenant,
            is_primary=False
        )
        
        # Test domain lookup
        found_tenant_primary = Domain.objects.get(domain='testcorp.localhost').tenant
        found_tenant_alias = Domain.objects.get(domain='testcorp.com').tenant
        
        self.assertEqual(found_tenant_primary, tenant)
        self.assertEqual(found_tenant_alias, tenant)
        
        # Test primary domain identification
        primary = tenant.domains.filter(is_primary=True).first()
        self.assertEqual(primary, primary_domain)
