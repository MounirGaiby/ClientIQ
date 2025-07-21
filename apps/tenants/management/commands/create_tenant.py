from django.core.management.base import BaseCommand
from django.db import transaction
from apps.tenants.models import Tenant, Domain
from apps.users.models import User
from apps.permissions.models import Role, RoleGroup, Permission


class Command(BaseCommand):
    help = 'Create a new tenant with admin user and basic setup'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Tenant name')
        parser.add_argument('--schema', type=str, help='Schema name')
        parser.add_argument('--domain', type=str, help='Domain name')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')

    def handle(self, *args, **options):
        name = options.get('name') or input('Tenant name: ')
        schema_name = options.get('schema') or input('Schema name: ')
        domain_name = options.get('domain') or input('Domain name: ')
        admin_email = options.get('email') or input('Admin email: ')
        admin_password = options.get('password') or input('Admin password: ')

        with transaction.atomic():
            # Create tenant
            tenant = Tenant(
                name=name,
                schema_name=schema_name,
                contact_email=admin_email
            )
            tenant.save()

            # Create domain
            domain = Domain(
                domain=domain_name,
                tenant=tenant,
                is_primary=True
            )
            domain.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created tenant "{name}" with schema "{schema_name}"')
            )

            # Create tenant schema and run migrations
            from django.core.management import call_command
            from django_tenants.utils import schema_context
            
            # Run tenant migrations
            call_command('migrate_schemas', '--tenant', schema_name)
            
            # Switch to tenant schema and create admin user with roles
            with schema_context(schema_name):
                # Create role groups
                admin_group, _ = RoleGroup.objects.get_or_create(
                    name='Administrators',
                    defaults={'description': 'System administrators with full access'}
                )
                
                managers_group, _ = RoleGroup.objects.get_or_create(
                    name='Managers',
                    defaults={'description': 'Managers with elevated permissions'}
                )
                
                users_group, _ = RoleGroup.objects.get_or_create(
                    name='Users',
                    defaults={'description': 'Regular users with basic permissions'}
                )
                
                # Create basic permissions
                permissions_data = [
                    # User permissions
                    ('users_user_create', 'Create users', 'users', 'user', 'create'),
                    ('users_user_read', 'View users', 'users', 'user', 'read'),
                    ('users_user_update', 'Update users', 'users', 'user', 'update'),
                    ('users_user_delete', 'Delete users', 'users', 'user', 'delete'),
                    
                    # Role permissions
                    ('permissions_role_create', 'Create roles', 'permissions', 'role', 'create'),
                    ('permissions_role_read', 'View roles', 'permissions', 'role', 'read'),
                    ('permissions_role_update', 'Update roles', 'permissions', 'role', 'update'),
                    ('permissions_role_delete', 'Delete roles', 'permissions', 'role', 'delete'),
                    
                    # Permission permissions
                    ('permissions_permission_read', 'View permissions', 'permissions', 'permission', 'read'),
                    
                    # Tenant settings
                    ('tenants_settings_read', 'View tenant settings', 'tenants', 'settings', 'read'),
                    ('tenants_settings_update', 'Update tenant settings', 'tenants', 'settings', 'update'),
                ]
                
                created_permissions = []
                for codename, name, module, resource, perm_type in permissions_data:
                    permission, _ = Permission.objects.get_or_create(
                        codename=codename,
                        defaults={
                            'name': name,
                            'module': module,
                            'resource': resource,
                            'permission_type': perm_type,
                            'is_system': True
                        }
                    )
                    created_permissions.append(permission)
                
                # Create admin role with all permissions
                admin_role, _ = Role.objects.get_or_create(
                    name='Tenant Administrator',
                    defaults={
                        'description': 'Full administrative access to tenant',
                        'role_group': admin_group,
                        'is_system': True
                    }
                )
                admin_role.permissions.set(created_permissions)
                
                # Create manager role with limited permissions
                manager_permissions = [p for p in created_permissions if p.permission_type != 'delete']
                manager_role, _ = Role.objects.get_or_create(
                    name='Manager',
                    defaults={
                        'description': 'Management access with limited permissions',
                        'role_group': managers_group,
                        'is_system': True
                    }
                )
                manager_role.permissions.set(manager_permissions)
                
                # Create user role with read permissions
                user_permissions = [p for p in created_permissions if p.permission_type == 'read']
                user_role, _ = Role.objects.get_or_create(
                    name='User',
                    defaults={
                        'description': 'Basic user with read-only access',
                        'role_group': users_group,
                        'is_system': True
                    }
                )
                user_role.permissions.set(user_permissions)
                
                # Create admin user
                admin_user = User.objects.create_tenant_admin(
                    email=admin_email,
                    password=admin_password,
                    first_name='Admin',
                    last_name='User'
                )
                
                # Assign admin role to user
                admin_role.users.add(admin_user)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created admin user "{admin_email}" with Tenant Administrator role'
                    )
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Tenant setup complete!\n'
                        f'- Tenant: {name}\n'
                        f'- Schema: {schema_name}\n'
                        f'- Domain: {domain_name}\n'
                        f'- Admin: {admin_email}\n'
                        f'- Roles created: {Role.objects.count()}\n'
                        f'- Permissions created: {Permission.objects.count()}'
                    )
                )
