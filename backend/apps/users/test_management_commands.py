"""
Comprehensive tests for management commands.
Tests setup_simple_tenant, clean_tenant_permissions, and other commands.
"""

from django.test import TestCase, TransactionTestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import schema_context, tenant_context
from io import StringIO
import sys

from apps.tenants.models import Tenant, Domain
from apps.users.models import CustomUser
from apps.platform.models import SuperUser
from apps.demo.models import DemoRequest


class SetupSimpleTenantCommandTest(TransactionTestCase):
    """Test setup_simple_tenant management command."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant for testing
        self.tenant = Tenant.objects.create(
            schema_name='testcommand',
            name='Test Command Corp',
            contact_email='admin@testcommand.com'
        )
        
        self.domain = Domain.objects.create(
            domain='testcommand.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_setup_simple_tenant_creates_users(self):
        """Test that setup_simple_tenant creates default users."""
        # Run command
        call_command('setup_simple_tenant', schema='testcommand')
        
        # Check that users were created in tenant schema
        with tenant_context(self.tenant):
            admin_user = CustomUser.objects.filter(email='admin@testcommand.com').first()
            manager_user = CustomUser.objects.filter(email='manager@testcommand.com').first()
            regular_user = CustomUser.objects.filter(email='user@testcommand.com').first()
            
            self.assertIsNotNone(admin_user)
            self.assertIsNotNone(manager_user)
            self.assertIsNotNone(regular_user)
            
            # Check user properties
            self.assertTrue(admin_user.is_admin)
            self.assertEqual(admin_user.user_type, 'admin')
            
            self.assertFalse(manager_user.is_admin)
            self.assertEqual(manager_user.user_type, 'manager')
            
            self.assertFalse(regular_user.is_admin)
            self.assertEqual(regular_user.user_type, 'user')
    
    def test_setup_simple_tenant_creates_groups(self):
        """Test that setup_simple_tenant creates default groups."""
        # Run command
        call_command('setup_simple_tenant', schema='testcommand')
        
        # Check that groups were created
        with tenant_context(self.tenant):
            admin_group = Group.objects.filter(name='Administrators').first()
            manager_group = Group.objects.filter(name='Managers').first()
            user_group = Group.objects.filter(name='Users').first()
            
            self.assertIsNotNone(admin_group)
            self.assertIsNotNone(manager_group)
            self.assertIsNotNone(user_group)
    
    def test_setup_simple_tenant_assigns_users_to_groups(self):
        """Test that setup_simple_tenant assigns users to appropriate groups."""
        # Run command
        call_command('setup_simple_tenant', schema='testcommand')
        
        # Check user group assignments
        with tenant_context(self.tenant):
            admin_user = CustomUser.objects.get(email='admin@testcommand.com')
            manager_user = CustomUser.objects.get(email='manager@testcommand.com')
            regular_user = CustomUser.objects.get(email='user@testcommand.com')
            
            admin_group = Group.objects.get(name='Administrators')
            manager_group = Group.objects.get(name='Managers')
            user_group = Group.objects.get(name='Users')
            
            self.assertIn(admin_group, admin_user.groups.all())
            self.assertIn(manager_group, manager_user.groups.all())
            self.assertIn(user_group, regular_user.groups.all())
    
    def test_setup_simple_tenant_with_nonexistent_schema(self):
        """Test setup_simple_tenant with non-existent schema."""
        with self.assertRaises(CommandError):
            call_command('setup_simple_tenant', schema='nonexistent')
    
    def test_setup_simple_tenant_idempotent(self):
        """Test that setup_simple_tenant is idempotent."""
        # Run command twice
        call_command('setup_simple_tenant', schema='testcommand')
        call_command('setup_simple_tenant', schema='testcommand')
        
        # Should not create duplicate users
        with tenant_context(self.tenant):
            admin_users = CustomUser.objects.filter(email='admin@testcommand.com')
            self.assertEqual(admin_users.count(), 1)
    
    def test_setup_simple_tenant_output(self):
        """Test setup_simple_tenant command output."""
        # Capture stdout
        out = StringIO()
        call_command('setup_simple_tenant', schema='testcommand', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Setting up simple tenant for schema: testcommand', output)
        self.assertIn('Created user:', output)
        self.assertIn('Created group:', output)


class CleanTenantPermissionsCommandTest(TransactionTestCase):
    """Test clean_tenant_permissions management command."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant for testing
        self.tenant = Tenant.objects.create(
            schema_name='cleantest',
            name='Clean Test Corp',
            contact_email='admin@cleantest.com'
        )
        
        self.domain = Domain.objects.create(
            domain='cleantest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
    
    def test_clean_tenant_permissions_removes_platform_permissions(self):
        """Test that clean_tenant_permissions removes platform-specific permissions."""
        # First, migrate tenant schema to get all permissions
        with tenant_context(self.tenant):
            # Count initial permissions
            initial_permission_count = Permission.objects.count()
            
            # Run clean command
            call_command('clean_tenant_permissions', schema='cleantest')
            
            # Count permissions after cleaning
            final_permission_count = Permission.objects.count()
            
            # Should have fewer permissions
            self.assertLess(final_permission_count, initial_permission_count)
            
            # Check that specific platform permissions are removed
            platform_permissions = Permission.objects.filter(
                content_type__app_label__in=[
                    'admin', 'platform', 'tenants', 'demo', 
                    'token_blacklist', 'sessions'
                ]
            )
            self.assertEqual(platform_permissions.count(), 0)
    
    def test_clean_tenant_permissions_preserves_tenant_permissions(self):
        """Test that clean_tenant_permissions preserves tenant-relevant permissions."""
        with tenant_context(self.tenant):
            # Run clean command
            call_command('clean_tenant_permissions', schema='cleantest')
            
            # Check that tenant permissions remain
            user_permissions = Permission.objects.filter(
                content_type__app_label='users'
            )
            auth_permissions = Permission.objects.filter(
                content_type__app_label='auth'
            )
            
            self.assertGreater(user_permissions.count(), 0)
            self.assertGreater(auth_permissions.count(), 0)
    
    def test_clean_tenant_permissions_with_nonexistent_schema(self):
        """Test clean_tenant_permissions with non-existent schema."""
        with self.assertRaises(CommandError):
            call_command('clean_tenant_permissions', schema='nonexistent')
    
    def test_clean_tenant_permissions_output(self):
        """Test clean_tenant_permissions command output."""
        # Capture stdout
        out = StringIO()
        call_command('clean_tenant_permissions', schema='cleantest', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Cleaning permissions for tenant schema: cleantest', output)
        self.assertIn('Removed', output)
        self.assertIn('permissions', output)
    
    def test_clean_tenant_permissions_idempotent(self):
        """Test that clean_tenant_permissions is idempotent."""
        with tenant_context(self.tenant):
            # Run command twice
            call_command('clean_tenant_permissions', schema='cleantest')
            count_after_first = Permission.objects.count()
            
            call_command('clean_tenant_permissions', schema='cleantest')
            count_after_second = Permission.objects.count()
            
            # Count should be the same
            self.assertEqual(count_after_first, count_after_second)


class ConvertDemoToTenantCommandTest(TransactionTestCase):
    """Test convert_demo_to_tenant management command."""
    
    def setUp(self):
        """Set up test data."""
        # Create demo request
        self.demo = DemoRequest.objects.create(
            company_name='Demo Corporation',
            contact_email='admin@democorp.com',
            contact_name='Demo Admin',
            phone_number='+1234567890',
            message='We want to convert to tenant',
            status='approved'
        )
    
    def test_convert_demo_to_tenant_creates_tenant(self):
        """Test that convert_demo_to_tenant creates tenant and domain."""
        # Run command
        call_command(
            'convert_demo_to_tenant',
            str(self.demo.id),
            'democorp',
            'democorp.localhost'
        )
        
        # Check that tenant was created
        tenant = Tenant.objects.filter(schema_name='democorp').first()
        self.assertIsNotNone(tenant)
        self.assertEqual(tenant.name, 'Demo Corporation')
        self.assertEqual(tenant.contact_email, 'admin@democorp.com')
        
        # Check that domain was created
        domain = Domain.objects.filter(domain='democorp.localhost').first()
        self.assertIsNotNone(domain)
        self.assertEqual(domain.tenant, tenant)
        self.assertTrue(domain.is_primary)
    
    def test_convert_demo_to_tenant_creates_admin_user(self):
        """Test that convert_demo_to_tenant creates admin user in tenant schema."""
        # Run command
        call_command(
            'convert_demo_to_tenant',
            str(self.demo.id),
            'democorp',
            'democorp.localhost'
        )
        
        # Check that admin user was created in tenant schema
        tenant = Tenant.objects.get(schema_name='democorp')
        with tenant_context(tenant):
            admin_user = CustomUser.objects.filter(email='admin@democorp.com').first()
            self.assertIsNotNone(admin_user)
            self.assertTrue(admin_user.is_admin)
            self.assertEqual(admin_user.first_name, 'Demo')
            self.assertEqual(admin_user.last_name, 'Admin')
    
    def test_convert_demo_to_tenant_updates_demo_status(self):
        """Test that convert_demo_to_tenant updates demo status to converted."""
        # Run command
        call_command(
            'convert_demo_to_tenant',
            str(self.demo.id),
            'democorp',
            'democorp.localhost'
        )
        
        # Check that demo status was updated
        self.demo.refresh_from_db()
        self.assertEqual(self.demo.status, 'converted')
    
    def test_convert_demo_to_tenant_cleans_permissions(self):
        """Test that convert_demo_to_tenant cleans tenant permissions."""
        # Run command
        call_command(
            'convert_demo_to_tenant',
            str(self.demo.id),
            'democorp',
            'democorp.localhost'
        )
        
        # Check that permissions were cleaned
        tenant = Tenant.objects.get(schema_name='democorp')
        with tenant_context(tenant):
            platform_permissions = Permission.objects.filter(
                content_type__app_label__in=[
                    'admin', 'platform', 'tenants', 'demo'
                ]
            )
            self.assertEqual(platform_permissions.count(), 0)
    
    def test_convert_demo_to_tenant_with_nonexistent_demo(self):
        """Test convert_demo_to_tenant with non-existent demo ID."""
        with self.assertRaises(CommandError):
            call_command(
                'convert_demo_to_tenant',
                '99999',
                'democorp',
                'democorp.localhost'
            )
    
    def test_convert_demo_to_tenant_with_existing_schema(self):
        """Test convert_demo_to_tenant with existing schema name."""
        # Create existing tenant
        Tenant.objects.create(
            schema_name='democorp',
            name='Existing Corp',
            contact_email='existing@corp.com'
        )
        
        # Try to convert demo with same schema name
        with self.assertRaises(CommandError):
            call_command(
                'convert_demo_to_tenant',
                str(self.demo.id),
                'democorp',
                'democorp.localhost'
            )
    
    def test_convert_demo_to_tenant_with_existing_domain(self):
        """Test convert_demo_to_tenant with existing domain."""
        # Create existing tenant with domain
        existing_tenant = Tenant.objects.create(
            schema_name='existing',
            name='Existing Corp',
            contact_email='existing@corp.com'
        )
        Domain.objects.create(
            domain='democorp.localhost',
            tenant=existing_tenant,
            is_primary=True
        )
        
        # Try to convert demo with same domain
        with self.assertRaises(CommandError):
            call_command(
                'convert_demo_to_tenant',
                str(self.demo.id),
                'democorp2',
                'democorp.localhost'
            )
    
    def test_convert_demo_to_tenant_output(self):
        """Test convert_demo_to_tenant command output."""
        # Capture stdout
        out = StringIO()
        call_command(
            'convert_demo_to_tenant',
            str(self.demo.id),
            'democorp',
            'democorp.localhost',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Converting demo request', output)
        self.assertIn('Created tenant:', output)
        self.assertIn('Created domain:', output)
        self.assertIn('Created admin user:', output)
        self.assertIn('Cleaned tenant permissions', output)
        self.assertIn('Demo conversion completed', output)


class ManagementCommandIntegrationTest(TransactionTestCase):
    """Integration tests for management commands working together."""
    
    def test_full_tenant_setup_workflow(self):
        """Test full tenant setup workflow using multiple commands."""
        # 1. Create demo request
        demo = DemoRequest.objects.create(
            company_name='Integration Test Corp',
            contact_email='admin@integration.com',
            contact_name='Integration Admin',
            status='approved'
        )
        
        # 2. Convert demo to tenant
        call_command(
            'convert_demo_to_tenant',
            str(demo.id),
            'integration',
            'integration.localhost'
        )
        
        # 3. Setup additional tenant users
        call_command('setup_simple_tenant', schema='integration')
        
        # 4. Clean permissions again
        call_command('clean_tenant_permissions', schema='integration')
        
        # Verify final state
        tenant = Tenant.objects.get(schema_name='integration')
        domain = Domain.objects.get(domain='integration.localhost')
        
        self.assertEqual(domain.tenant, tenant)
        
        with tenant_context(tenant):
            # Should have admin user from conversion
            admin_user = CustomUser.objects.get(email='admin@integration.com')
            self.assertTrue(admin_user.is_admin)
            
            # Should have additional users from setup command
            manager_user = CustomUser.objects.filter(email='manager@integration.com').first()
            regular_user = CustomUser.objects.filter(email='user@integration.com').first()
            
            self.assertIsNotNone(manager_user)
            self.assertIsNotNone(regular_user)
            
            # Permissions should be clean
            platform_permissions = Permission.objects.filter(
                content_type__app_label__in=['platform', 'tenants', 'demo']
            )
            self.assertEqual(platform_permissions.count(), 0)
        
        # Demo should be marked as converted
        demo.refresh_from_db()
        self.assertEqual(demo.status, 'converted')
    
    def test_command_error_handling(self):
        """Test error handling across commands."""
        # Test setup_simple_tenant with invalid schema
        with self.assertRaises(CommandError):
            call_command('setup_simple_tenant', schema='nonexistent')
        
        # Test clean_tenant_permissions with invalid schema
        with self.assertRaises(CommandError):
            call_command('clean_tenant_permissions', schema='nonexistent')
        
        # Test convert_demo_to_tenant with invalid demo
        with self.assertRaises(CommandError):
            call_command(
                'convert_demo_to_tenant',
                '99999',
                'invalid',
                'invalid.localhost'
            )
    
    def test_command_help_text(self):
        """Test that commands have proper help text."""
        # Capture help output
        out = StringIO()
        
        # Test setup_simple_tenant help
        call_command('help', 'setup_simple_tenant', stdout=out)
        help_output = out.getvalue()
        self.assertIn('setup_simple_tenant', help_output)
        
        # Test clean_tenant_permissions help
        out = StringIO()
        call_command('help', 'clean_tenant_permissions', stdout=out)
        help_output = out.getvalue()
        self.assertIn('clean_tenant_permissions', help_output)
        
        # Test convert_demo_to_tenant help
        out = StringIO()
        call_command('help', 'convert_demo_to_tenant', stdout=out)
        help_output = out.getvalue()
        self.assertIn('convert_demo_to_tenant', help_output)


class CommandArgumentValidationTest(TestCase):
    """Test command argument validation."""
    
    def test_setup_simple_tenant_argument_validation(self):
        """Test setup_simple_tenant argument validation."""
        # Test missing schema argument
        with self.assertRaises(CommandError):
            call_command('setup_simple_tenant')
    
    def test_clean_tenant_permissions_argument_validation(self):
        """Test clean_tenant_permissions argument validation."""
        # Test missing schema argument
        with self.assertRaises(CommandError):
            call_command('clean_tenant_permissions')
    
    def test_convert_demo_to_tenant_argument_validation(self):
        """Test convert_demo_to_tenant argument validation."""
        # Test missing arguments
        with self.assertRaises(CommandError):
            call_command('convert_demo_to_tenant')
        
        # Test insufficient arguments
        with self.assertRaises(CommandError):
            call_command('convert_demo_to_tenant', '1')
        
        with self.assertRaises(CommandError):
            call_command('convert_demo_to_tenant', '1', 'schema')
    
    def test_schema_name_validation(self):
        """Test schema name validation in commands."""
        # Create a demo for testing
        demo = DemoRequest.objects.create(
            company_name='Test Corp',
            contact_email='test@corp.com',
            contact_name='Test User',
            status='approved'
        )
        
        # Test invalid schema names
        invalid_schemas = ['public', 'information_schema', 'pg_catalog']
        
        for invalid_schema in invalid_schemas:
            with self.assertRaises(CommandError):
                call_command(
                    'convert_demo_to_tenant',
                    str(demo.id),
                    invalid_schema,
                    'test.localhost'
                )
