from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create a new tenant with domain'

    def add_arguments(self, parser):
        parser.add_argument('schema_name', type=str, help='Schema name for the tenant')
        parser.add_argument('domain', type=str, help='Domain for the tenant')
        parser.add_argument('name', type=str, help='Display name for the tenant')
        parser.add_argument('--email', type=str, default='admin@example.com', help='Contact email')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        domain_name = options['domain']
        name = options['name']
        email = options['email']

        # Create tenant
        tenant = Tenant.objects.create(
            schema_name=schema_name,
            name=name,
            contact_email=email,
            plan='trial',
            is_active=True
        )

        # Create domain
        domain = Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully created tenant "{name}" with schema "{schema_name}" and domain "{domain_name}"'
            )
        )
        
        # Run migrations for this tenant
        self.stdout.write('🔄 Running tenant migrations...')
        from django.core.management import call_command
        call_command('migrate_schemas', schema_name=schema_name, verbosity=1)
        
        self.stdout.write(self.style.SUCCESS('🎉 Tenant setup complete!'))
