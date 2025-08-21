from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils import timezone
from django_tenants.utils import schema_context, tenant_context
from apps.tenants.models import Tenant, Domain
from apps.contacts.models import Company, Contact
from apps.demo.models import DemoRequest
from apps.platform.models import SuperUser
from apps.users.models import CustomUser
import random

# For public schema (platform)
PlatformUser = SuperUser
# For tenant schemas
TenantUser = CustomUser


class Command(BaseCommand):
    help = 'Complete seed data: creates superuser, tenant with users, groups, permissions, and sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting comprehensive seed...'))
        
        with transaction.atomic():
            # Step 1: Create superuser (in public schema)
            superuser_credentials = self.create_superuser()
            
            # Step 2: Create tenant and domain
            tenant = self.create_tenant()
            
            # Step 3: Switch to tenant schema and create tenant data
            with tenant_context(tenant):
                tenant_admin_credentials = self.create_tenant_data()
                
                # Step 4: Create sample business data
                self.create_sample_data()
        
        # Print credentials at the end
        self.print_credentials(superuser_credentials, tenant_admin_credentials)
        
        self.stdout.write(self.style.SUCCESS('🎉 Comprehensive seed completed successfully!'))

    def create_superuser(self):
        """Create platform superuser"""
        self.stdout.write('👑 Creating platform superuser...')
        
        # Check if superuser already exists
        if PlatformUser.objects.filter(email='admin@platform.com').exists():
            self.stdout.write('⏭️  Superuser already exists')
            return {
                'email': 'admin@platform.com',
                'password': '****existing****'
            }
        
        superuser = PlatformUser.objects.create_superuser(
            email='admin@platform.com',
            password='platform123',
            first_name='Platform',
            last_name='Administrator'
        )
        
        self.stdout.write(f'✅ Created superuser: {superuser.email}')
        return {
            'email': 'admin@platform.com',
            'password': 'platform123'
        }

    def create_tenant(self):
        """Create tenant and domain"""
        self.stdout.write('🏢 Creating tenant and domain...')
        
        # Create or get tenant
        tenant, created = Tenant.objects.get_or_create(
            schema_name='acme',
            defaults={
                'name': 'ACME Corporation',
                'contact_email': 'admin@acme.com',
                'industry': 'Technology',
                'company_size': '51-200'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Created tenant: {tenant.name}')
        else:
            self.stdout.write(f'⏭️  Tenant {tenant.name} already exists')
        
        # Create or get domain
        domain, created = Domain.objects.get_or_create(
            domain='acme.localhost',
            defaults={
                'tenant': tenant,
                'is_primary': True
            }
        )
        
        if created:
            self.stdout.write(f'✅ Created domain: {domain.domain}')
        else:
            self.stdout.write(f'⏭️  Domain {domain.domain} already exists')
        
        return tenant

    def create_tenant_data(self):
        """Create groups, permissions, and users in tenant schema"""
        self.stdout.write('👥 Creating tenant groups and users...')
        
        # Create groups with different permission levels
        groups = self.create_groups()
        
        # Create users and assign to groups
        admin_credentials = self.create_users(groups)
        
        return admin_credentials

    def create_groups(self):
        """Create tenant groups with appropriate permissions"""
        groups_data = {
            'Admin': {
                'description': 'Full tenant administration access',
                'permissions': 'all_tenant'
            },
            'Manager': {
                'description': 'Management level access',
                'permissions': 'management'
            },
            'Sales': {
                'description': 'Sales team access',
                'permissions': 'sales'
            },
            'Support': {
                'description': 'Customer support access',
                'permissions': 'support'
            },
            'User': {
                'description': 'Basic user access',
                'permissions': 'basic'
            }
        }
        
        created_groups = {}
        
        for group_name, group_info in groups_data.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.assign_permissions_to_group(group, group_info['permissions'])
                self.stdout.write(f'✅ Created group: {group_name}')
            else:
                self.stdout.write(f'⏭️  Group {group_name} already exists')
            
            created_groups[group_name] = group
        
        return created_groups

    def assign_permissions_to_group(self, group, permission_level):
        """Assign permissions based on the permission level"""
        all_permissions = Permission.objects.all()
        
        if permission_level == 'all_tenant':
            # Admin gets all tenant permissions except superuser-only ones
            tenant_permissions = all_permissions.exclude(
                codename__in=[
                    'add_tenant', 'change_tenant', 'delete_tenant', 'view_tenant',
                    'add_domain', 'change_domain', 'delete_domain', 'view_domain',
                ]
            )
            group.permissions.set(tenant_permissions)
            
        elif permission_level == 'management':
            # Managers get user and content management permissions
            manager_permissions = all_permissions.filter(
                codename__in=[
                    'view_customuser', 'change_customuser',
                    'add_contact', 'change_contact', 'delete_contact', 'view_contact',
                    'add_company', 'change_company', 'delete_company', 'view_company',
                    'view_demorequest', 'change_demorequest'
                ]
            )
            group.permissions.set(manager_permissions)
            
        elif permission_level == 'sales':
            # Sales team gets contact and company access
            sales_permissions = all_permissions.filter(
                codename__in=[
                    'add_contact', 'change_contact', 'view_contact',
                    'add_company', 'change_company', 'view_company',
                    'view_customuser'
                ]
            )
            group.permissions.set(sales_permissions)
            
        elif permission_level == 'support':
            # Support gets read access and demo request management
            support_permissions = all_permissions.filter(
                codename__in=[
                    'view_contact', 'view_company',
                    'add_demorequest', 'change_demorequest', 'view_demorequest',
                    'view_customuser'
                ]
            )
            group.permissions.set(support_permissions)
            
        elif permission_level == 'basic':
            # Basic users get minimal read access
            basic_permissions = all_permissions.filter(
                codename__in=[
                    'view_contact', 'view_company', 'view_customuser'
                ]
            )
            group.permissions.set(basic_permissions)

    def create_users(self, groups):
        """Create users with different roles"""
        users_data = [
            {
                'email': 'admin@acme.com',
                'password': 'admin123',
                'first_name': 'John',
                'last_name': 'Admin',
                'job_title': 'Tenant Administrator',
                'department': 'Management',
                'groups': ['Admin'],
                'is_admin': True
            },
            {
                'email': 'manager@acme.com',
                'password': 'manager123',
                'first_name': 'Sarah',
                'last_name': 'Manager',
                'job_title': 'Sales Manager',
                'department': 'Sales',
                'groups': ['Manager', 'Sales']
            },
            {
                'email': 'sales1@acme.com',
                'password': 'sales123',
                'first_name': 'Mike',
                'last_name': 'Thompson',
                'job_title': 'Senior Sales Representative',
                'department': 'Sales',
                'groups': ['Sales']
            },
            {
                'email': 'sales2@acme.com',
                'password': 'sales123',
                'first_name': 'Lisa',
                'last_name': 'Rodriguez',
                'job_title': 'Sales Representative',
                'department': 'Sales',
                'groups': ['Sales']
            },
            {
                'email': 'support@acme.com',
                'password': 'support123',
                'first_name': 'David',
                'last_name': 'Support',
                'job_title': 'Customer Support Specialist',
                'department': 'Support',
                'groups': ['Support']
            },
            {
                'email': 'user@acme.com',
                'password': 'user123',
                'first_name': 'Emma',
                'last_name': 'User',
                'job_title': 'Marketing Coordinator',
                'department': 'Marketing',
                'groups': ['User']
            }
        ]
        
        admin_credentials = None
        
        for user_data in users_data:
            if not TenantUser.objects.filter(email=user_data['email']).exists():
                user = TenantUser.objects.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    job_title=user_data['job_title'],
                    department=user_data['department'],
                    is_admin=user_data.get('is_admin', False)
                )
                
                # Add user to groups
                for group_name in user_data['groups']:
                    if group_name in groups:
                        user.groups.add(groups[group_name])
                
                self.stdout.write(f'✅ Created user: {user.email} ({user.job_title})')
                
                # Store admin credentials
                if 'Admin' in user_data['groups']:
                    admin_credentials = {
                        'email': user_data['email'],
                        'password': user_data['password']
                    }
            else:
                self.stdout.write(f'⏭️  User {user_data["email"]} already exists')
        
        return admin_credentials or {'email': 'admin@acme.com', 'password': '****existing****'}

    def create_sample_data(self):
        """Create sample business data"""
        self.stdout.write('📊 Creating sample business data...')
        
        # Create sample companies
        companies_data = [
            {
                'name': 'TechStart Inc.',
                'industry': 'Technology',
                'website': 'https://techstart.com',
                'phone': '+1-555-0101',
                'address_line1': '123 Tech Street',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'size': '11-50'
            },
            {
                'name': 'Global Solutions Ltd.',
                'industry': 'Consulting',
                'website': 'https://globalsolutions.com',
                'phone': '+1-555-0102',
                'address_line1': '456 Business Ave',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'size': '51-200'
            },
            {
                'name': 'Innovation Labs',
                'industry': 'Research',
                'website': 'https://innovationlabs.com',
                'phone': '+1-555-0103',
                'address_line1': '789 Research Blvd',
                'city': 'Austin',
                'state': 'TX',
                'country': 'USA',
                'size': '1-10'
            }
        ]
        
        companies = []
        for company_data in companies_data:
            company, created = Company.objects.get_or_create(
                name=company_data['name'],
                defaults=company_data
            )
            companies.append(company)
            if created:
                self.stdout.write(f'✅ Created company: {company.name}')
        
        # Create sample contacts
        contacts_data = [
            {
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice@techstart.com',
                'phone': '+1-555-1001',
                'job_title': 'CTO',
                'company': companies[0] if companies else None,
                'contact_type': 'lead'
            },
            {
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'email': 'bob@globalsolutions.com',
                'phone': '+1-555-1002',
                'job_title': 'CEO',
                'company': companies[1] if len(companies) > 1 else None,
                'contact_type': 'customer'
            },
            {
                'first_name': 'Carol',
                'last_name': 'Smith',
                'email': 'carol@innovationlabs.com',
                'phone': '+1-555-1003',
                'job_title': 'Research Director',
                'company': companies[2] if len(companies) > 2 else None,
                'contact_type': 'prospect'
            }
        ]
        
        # Assign random owners (sales users)
        sales_users = TenantUser.objects.filter(groups__name='Sales')
        
        for contact_data in contacts_data:
            if not Contact.objects.filter(email=contact_data['email']).exists():
                if sales_users.exists():
                    contact_data['owner'] = random.choice(sales_users)
                
                contact = Contact.objects.create(**contact_data)
                self.stdout.write(f'✅ Created contact: {contact.first_name} {contact.last_name}')

        # Create sample demo requests
        demo_requests = [
            {
                'company_name': 'Future Systems',
                'first_name': 'Robert',
                'last_name': 'Brown',
                'email': 'robert@futuresystems.com',
                'phone': '+1-555-2001',
                'job_title': 'VP Technology',
                'company_size': '201-500',
                'industry': 'Software',
                'message': 'Interested in your CRM solution for our growing team.',
                'status': 'pending'
            },
            {
                'company_name': 'Startup Ventures',
                'first_name': 'Jennifer',
                'last_name': 'Davis',
                'email': 'jen@startupventures.com',
                'phone': '+1-555-2002',
                'job_title': 'Founder',
                'company_size': '1-10',
                'industry': 'Startup',
                'message': 'Looking for an affordable CRM solution.',
                'status': 'processing'
            }
        ]
        
        for demo_data in demo_requests:
            demo, created = DemoRequest.objects.get_or_create(
                email=demo_data['email'],
                defaults=demo_data
            )
            if created:
                self.stdout.write(f'✅ Created demo request: {demo.company_name}')

    def print_credentials(self, superuser_creds, tenant_admin_creds):
        """Print login credentials"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🔑 LOGIN CREDENTIALS'))
        self.stdout.write('='*60)
        
        self.stdout.write('\n👑 PLATFORM SUPERUSER:')
        self.stdout.write(f'   Email: {superuser_creds["email"]}')
        self.stdout.write(f'   Password: {superuser_creds["password"]}')
        self.stdout.write('   Access: Django Admin, Platform Management')
        self.stdout.write('   URL: http://localhost:8000/admin/')
        
        self.stdout.write('\n🏢 TENANT ADMIN (ACME Corporation):')
        self.stdout.write(f'   Email: {tenant_admin_creds["email"]}')
        self.stdout.write(f'   Password: {tenant_admin_creds["password"]}')
        self.stdout.write('   Access: Full tenant permissions, All CRM features')
        self.stdout.write('   URL: http://acme.localhost:5173/')
        
        self.stdout.write('\n📋 OTHER TENANT USERS:')
        self.stdout.write('   manager@acme.com / manager123 (Sales Manager)')
        self.stdout.write('   sales1@acme.com / sales123 (Senior Sales Rep)')
        self.stdout.write('   sales2@acme.com / sales123 (Sales Rep)')
        self.stdout.write('   support@acme.com / support123 (Support Specialist)')
        self.stdout.write('   user@acme.com / user123 (Marketing Coordinator)')
        
        self.stdout.write('\n🌐 ACCESS URLS:')
        self.stdout.write('   Platform: http://localhost:8000/admin/')
        self.stdout.write('   Tenant: http://acme.localhost:5173/')
        self.stdout.write('   API: http://localhost:8000/api/v1/')
        
        self.stdout.write('\n' + '='*60)
