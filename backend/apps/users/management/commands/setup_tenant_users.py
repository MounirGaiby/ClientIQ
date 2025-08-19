from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup users and groups for a tenant (run with tenant_command)'

    def handle(self, *args, **options):
        self.stdout.write('👥 Setting up tenant users and groups...')
        
        # Create Admin Group with all tenant permissions
        admin_group, created = Group.objects.get_or_create(name='Tenant Admin')
        if created:
            # Get all permissions except superuser-only ones
            tenant_permissions = Permission.objects.exclude(
                codename__in=['add_user', 'change_user', 'delete_user', 'view_user']
            ).filter(
                content_type__app_label__in=['demo', 'users', 'auth', 'sessions']
            )
            admin_group.permissions.set(tenant_permissions)
            self.stdout.write(f'✅ Created Admin group with {tenant_permissions.count()} permissions')

        # Create Manager Group with limited permissions
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            manager_permissions = Permission.objects.filter(
                content_type__app_label='demo'
            )
            manager_group.permissions.set(manager_permissions)
            self.stdout.write(f'✅ Created Manager group with {manager_permissions.count()} permissions')

        # Create User Group with view-only permissions
        user_group, created = Group.objects.get_or_create(name='User')
        if created:
            user_permissions = Permission.objects.filter(
                codename__startswith='view_'
            ).exclude(
                content_type__app_label='auth'
            )
            user_group.permissions.set(user_permissions)
            self.stdout.write(f'✅ Created User group with {user_permissions.count()} permissions')

        # 1. Admin User
        admin_user, created = User.objects.get_or_create(
            email='admin@acme.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'department': 'IT',
                'job_title': 'System Administrator',
                'is_tenant_admin': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        admin_user.groups.add(admin_group)
        self.stdout.write(f'✅ {"Created" if created else "Updated"} admin user: {admin_user.email}')

        # 2. Manager User  
        manager_user, created = User.objects.get_or_create(
            email='manager@acme.com',
            defaults={
                'first_name': 'Manager',
                'last_name': 'User',
                'user_type': 'manager',
                'department': 'Sales',
                'job_title': 'Sales Manager'
            }
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
        manager_user.groups.add(manager_group)
        self.stdout.write(f'✅ {"Created" if created else "Updated"} manager user: {manager_user.email}')

        # 3. Normal User
        normal_user, created = User.objects.get_or_create(
            email='user@acme.com',
            defaults={
                'first_name': 'Normal',
                'last_name': 'User',
                'user_type': 'user',
                'department': 'Sales',
                'job_title': 'Sales Representative'
            }
        )
        if created:
            normal_user.set_password('user123')
            normal_user.save()
        normal_user.groups.add(user_group)
        self.stdout.write(f'✅ {"Created" if created else "Updated"} normal user: {normal_user.email}')

        self.stdout.write('🎉 Tenant users setup complete!')
