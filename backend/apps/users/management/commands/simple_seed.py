from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db import connection
from apps.users.models import CustomUser  # Use specific model for tenant users

User = CustomUser  # Override the get_user_model() issue


class Command(BaseCommand):
    help = 'Create simplified seed data with 3 users + 1 superuser in ACME tenant'

    def handle(self, *args, **options):
        schema_name = connection.schema_name
        self.stdout.write(self.style.SUCCESS(f'🌱 Creating simplified seed for tenant: {schema_name}'))
        
        # Create tenant admin group with all tenant permissions (non-superuser only)
        self.create_tenant_admin_group()
        
        # Create the 4 users as requested
        self.create_users()
        
        self.stdout.write(self.style.SUCCESS(f'🎉 Simple seed completed for {schema_name}!'))

    def create_tenant_admin_group(self):
        """Create admin group with all tenant-based permissions (excluding superuser permissions)"""
        admin_group, created = Group.objects.get_or_create(name='Tenant Admin')
        
        if created:
            # Get all permissions except superuser-only ones and Django system permissions
            tenant_permissions = Permission.objects.exclude(
                codename__in=[
                    # Django system permissions that should not be in tenant schemas
                    'add_permission', 'change_permission', 'delete_permission', 'view_permission',
                    'add_group', 'change_group', 'delete_group', 'view_group',
                    'add_contenttype', 'change_contenttype', 'delete_contenttype', 'view_contenttype',
                    
                    # Superuser-only permissions (tenant management)
                    'add_tenant', 'change_tenant', 'delete_tenant', 'view_tenant',
                    'add_domain', 'change_domain', 'delete_domain', 'view_domain',
                    'add_superuser', 'change_superuser', 'delete_superuser', 'view_superuser',
                    
                    # Other platform-only permissions
                    'add_superuseronlypermission', 'change_superuseronlypermission', 
                    'delete_superuseronlypermission', 'view_superuseronlypermission',
                ]
            )
            
            admin_group.permissions.set(tenant_permissions)
            self.stdout.write(f'✅ Created Tenant Admin group with {tenant_permissions.count()} permissions')
            self.stdout.write('🔒 Superuser-only permissions excluded from tenant schema')
        else:
            self.stdout.write('⏭️  Tenant Admin group already exists')

    def create_users(self):
        """Create exactly 4 users: admin, manager, user, and superuser"""
        
        # 1. Tenant Admin (with Tenant Admin group)
        if not User.objects.filter(email='admin@acme.com').exists():
            admin_user = User.objects.create_user(
                email='admin@acme.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                department='Management',
                job_title='Tenant Administrator',
                is_admin=True  # Using our simplified flag
            )
            # Add to tenant admin group
            admin_group = Group.objects.get(name='Tenant Admin')
            admin_user.groups.add(admin_group)
            self.stdout.write(f'✅ Created tenant admin: {admin_user.email}')
        else:
            self.stdout.write('⏭️  Admin user already exists')

        # 2. Manager
        if not User.objects.filter(email='manager@acme.com').exists():
            manager_user = User.objects.create_user(
                email='manager@acme.com',
                password='manager123',
                first_name='Manager',
                last_name='User',
                department='Sales',
                job_title='Sales Manager',
                is_admin=False  # Regular manager, not admin
            )
            self.stdout.write(f'✅ Created manager: {manager_user.email}')
        else:
            self.stdout.write('⏭️  Manager user already exists')

        # 3. Regular User
        if not User.objects.filter(email='user@acme.com').exists():
            regular_user = User.objects.create_user(
                email='user@acme.com',
                password='user123',
                first_name='Regular',
                last_name='User',
                department='Sales',
                job_title='Sales Representative',
                is_admin=False  # Regular user
            )
            self.stdout.write(f'✅ Created regular user: {regular_user.email}')
        else:
            self.stdout.write('⏭️  Regular user already exists')

        # 4. Admin User (tenant admin but cannot access Django admin)
        if not User.objects.filter(email='superuser@acme.com').exists():
            super_user = User.objects.create_user(
                email='superuser@acme.com',
                password='super123',
                first_name='Super',
                last_name='User',
                department='IT',
                job_title='System Administrator',
                is_admin=True  # Tenant admin (but cannot access Django admin)
            )
            self.stdout.write(f'✅ Created admin user: {super_user.email}')
        else:
            self.stdout.write('⏭️  Admin user already exists')

        # Summary
        self.stdout.write('\n📊 User Summary:')
        for user in User.objects.all():
            groups = ', '.join([g.name for g in user.groups.all()]) or 'None'
            admin_status = 'Admin' if user.is_admin else 'Regular'
            self.stdout.write(f'  - {user.email} ({user.job_title}) - {admin_status} - Groups: {groups}')
