from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import connection

User = get_user_model()


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
            # Get all permissions except superuser-only ones
            tenant_permissions = Permission.objects.exclude(
                codename__in=[
                    'add_permission', 'change_permission', 'delete_permission', 'view_permission',
                    'add_group', 'change_group', 'delete_group', 'view_group',
                    'add_contenttype', 'change_contenttype', 'delete_contenttype', 'view_contenttype'
                ]
            )
            
            admin_group.permissions.set(tenant_permissions)
            self.stdout.write(f'✅ Created Tenant Admin group with {tenant_permissions.count()} permissions')
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
                user_type='admin',
                is_staff=False,  # Not Django admin access
                is_superuser=False,
                department='Management',
                job_title='Tenant Administrator',
                is_tenant_admin=True
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
                user_type='manager',
                is_staff=False,
                is_superuser=False,
                department='Sales',
                job_title='Sales Manager'
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
                user_type='user',
                is_staff=False,
                is_superuser=False,
                department='Sales',
                job_title='Sales Representative'
            )
            self.stdout.write(f'✅ Created regular user: {regular_user.email}')
        else:
            self.stdout.write('⏭️  Regular user already exists')

        # 4. Superuser (can access Django admin)
        if not User.objects.filter(email='superuser@acme.com').exists():
            super_user = User.objects.create_user(
                email='superuser@acme.com',
                password='super123',
                first_name='Super',
                last_name='User',
                user_type='admin',
                is_staff=True,  # Django admin access
                is_superuser=True,  # All permissions
                department='IT',
                job_title='System Administrator'
            )
            self.stdout.write(f'✅ Created superuser: {super_user.email}')
        else:
            self.stdout.write('⏭️  Superuser already exists')

        # Summary
        self.stdout.write('\n📊 User Summary:')
        for user in User.objects.all():
            groups = ', '.join([g.name for g in user.groups.all()]) or 'None'
            self.stdout.write(f'  - {user.email} ({user.user_type}) - Groups: {groups}')
