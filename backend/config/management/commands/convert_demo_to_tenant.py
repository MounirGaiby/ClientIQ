from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from apps.demo.models import DemoRequest
from apps.tenants.models import Tenant, Domain
from django.db import transaction
import re

User = get_user_model()


class Command(BaseCommand):
    help = 'Convert a demo request to a tenant with custom domain and admin user'

    def add_arguments(self, parser):
        parser.add_argument('demo_id', type=int, help='Demo request ID to convert')
        parser.add_argument('schema_name', type=str, help='Schema name for the new tenant')
        parser.add_argument('domain', type=str, help='Domain for the new tenant (e.g., company.localhost)')
        parser.add_argument('--admin-email', type=str, help='Admin email (default: use demo email)')
        parser.add_argument('--admin-password', type=str, default='admin123', help='Admin password (default: admin123)')

    def handle(self, *args, **options):
        demo_id = options['demo_id']
        schema_name = options['schema_name']
        domain_name = options['domain']
        admin_email = options['admin_email']
        admin_password = options['admin_password']
        
        try:
            # Get the demo request
            demo = DemoRequest.objects.get(id=demo_id)
            
            if demo.status == 'converted':
                self.stdout.write(self.style.ERROR(f'Demo {demo_id} is already converted'))
                return
                
            # Validate schema name (lowercase, no spaces, etc.)
            if not re.match(r'^[a-z][a-z0-9_]*$', schema_name):
                self.stdout.write(self.style.ERROR('Schema name must start with letter and contain only lowercase letters, numbers, and underscores'))
                return
                
            # Use demo email as admin email if not provided
            if not admin_email:
                admin_email = demo.email
                
            self.stdout.write(f'🚀 Converting demo {demo_id} to tenant...')
            self.stdout.write(f'   Company: {demo.company_name}')
            self.stdout.write(f'   Schema: {schema_name}')
            self.stdout.write(f'   Domain: {domain_name}')
            self.stdout.write(f'   Admin: {admin_email}')
            
            with transaction.atomic():
                # Create tenant
                tenant = Tenant.objects.create(
                    schema_name=schema_name,
                    name=demo.company_name,
                    contact_email=demo.email,
                    plan='trial',
                    is_active=True,
                    industry=demo.industry if hasattr(demo, 'industry') else '',
                    company_size=demo.company_size if hasattr(demo, 'company_size') else ''
                )
                
                # Create domain
                domain = Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )
                
                self.stdout.write(f'✅ Created tenant: {tenant.name} with schema {tenant.schema_name}')
                self.stdout.write(f'✅ Created domain: {domain.domain}')
                
                # Update demo status
                demo.status = 'converted'
                demo.notes = f'Converted to tenant {schema_name} on {tenant.created_at.strftime("%Y-%m-%d")}'
                demo.save()
                
                self.stdout.write(f'✅ Updated demo status to converted')
                
            # Now set up the tenant with admin user (this runs after tenant migration)
            self.setup_tenant_admin(schema_name, admin_email, admin_password, demo)
            
            self.stdout.write(self.style.SUCCESS(f'🎉 Demo {demo_id} successfully converted to tenant!'))
            self.stdout.write(f'🌐 Access at: http://{domain_name}:8000/')
            self.stdout.write(f'🔑 Admin login: {admin_email} / {admin_password}')
            
        except DemoRequest.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Demo request {demo_id} not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error converting demo: {str(e)}'))

    def setup_tenant_admin(self, schema_name, admin_email, admin_password, demo):
        """Set up admin user in the new tenant schema"""
        from django.core.management import call_command
        
        # Use tenant_command to run operations in the tenant schema
        try:
            # Create a temporary command file content
            command_content = f'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

# Create admin group with all tenant permissions (non-superuser)
admin_group, created = Group.objects.get_or_create(name='Admin')

if created:
    # Get all permissions for tenant apps, excluding superuser-only permissions
    tenant_permissions = Permission.objects.filter(
        content_type__app_label__in=[
            'users', 'auth', 'sessions'
        ]
    ).exclude(
        codename__in=[
            'add_permission', 'change_permission', 'delete_permission',
            'add_contenttype', 'change_contenttype', 'delete_contenttype'
        ]
    )
    
    admin_group.permissions.set(tenant_permissions)
    print(f"Created Admin group in {schema_name} with {{tenant_permissions.count()}} permissions")

# Create admin user
if not User.objects.filter(email="{admin_email}").exists():
    admin_user = User.objects.create_user(
        email="{admin_email}",
        password="{admin_password}",
        first_name="{demo.first_name}",
        last_name="{demo.last_name}",
        user_type='admin',
        is_staff=False,
        is_superuser=False,
        is_tenant_admin=True,
        job_title="{demo.job_title}",
        phone_number="{demo.phone}"
    )
    admin_user.groups.add(admin_group)
    
    print(f"Created tenant admin: {{admin_user.email}}")
else:
    print(f"Admin user {admin_email} already exists")
'''
            
            # Execute the command in tenant schema using shell
            call_command('tenant_command', 'shell', f'--schema={schema_name}', '-c', command_content)
            
        except Exception as e:
            self.stdout.write(f'⚠️  Warning: Could not set up admin user: {str(e)}')
            self.stdout.write(f'   You can manually create the admin user in the {schema_name} tenant')
