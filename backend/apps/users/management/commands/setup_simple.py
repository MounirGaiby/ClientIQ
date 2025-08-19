from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from apps.tenants.models import Tenant, Domain

User = get_user_model()


class Command(BaseCommand):
    help = 'Create simplified setup: one ACME tenant with 3 users + 1 superuser'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting simplified setup...'))
        
        # Create ACME tenant
        self.create_acme_tenant()
        
        # Create superuser in public schema
        self.create_superuser()
        
        self.stdout.write(self.style.SUCCESS('🎉 Setup completed!'))

    def create_acme_tenant(self):
        """Create ACME tenant with 3 users"""
        self.stdout.write('🏢 Setting up ACME tenant...')
        
        # Check if tenant exists
        try:
            tenant = Tenant.objects.get(schema_name='acme')
            self.stdout.write(f'⏭️  Tenant already exists: {tenant.name}')
        except Tenant.DoesNotExist:
            # Create tenant
            tenant = Tenant.objects.create(
                schema_name='acme',
                name='ACME Corporation',
                contact_email='admin@acme.com',
                plan='trial',
                is_active=True
            )

            # Create domain  
            domain = Domain.objects.create(
                domain='acme.localhost',
                tenant=tenant,
                is_primary=True
            )
            
            self.stdout.write(f'✅ Created tenant: {tenant.name} with domain {domain.domain}')
        
        # Create/update users using tenant_command to ensure they're in the right schema
        self.stdout.write('👥 Setting up ACME users...')
        from django.core.management import call_command
        call_command('tenant_command', 'setup_tenant_users', '--schema=acme')

    def create_superuser(self):
        """Create superuser in public schema for Django admin access"""
        self.stdout.write('👑 Setting up superuser...')
        
        superuser, created = User.objects.get_or_create(
            email='superuser@clientiq.com',
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'department': 'IT',
                'job_title': 'Platform Administrator'
            }
        )
        if created:
            superuser.set_password('super123')
            superuser.save()
        
        self.stdout.write(f'✅ {"Created" if created else "Updated"} superuser: {superuser.email}')
        
        self.stdout.write(self.style.WARNING('📝 Login Credentials:'))
        self.stdout.write('   🔑 Superuser (Django Admin): superuser@clientiq.com / super123')
        self.stdout.write('   🏢 Tenant Admin: admin@acme.com / admin123 (use acme.localhost)')
        self.stdout.write('   👔 Tenant Manager: manager@acme.com / manager123 (use acme.localhost)')
        self.stdout.write('   👤 Tenant User: user@acme.com / user123 (use acme.localhost)')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🚨 Important:'))
        self.stdout.write('   - Login only works on tenant domains (acme.localhost)')
        self.stdout.write('   - Base domain (localhost) blocks authentication')
        self.stdout.write('   - Superuser can access Django admin on any domain')
