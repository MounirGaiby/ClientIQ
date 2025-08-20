from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant, Domain
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a new tenant with domain'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Tenant name (e.g., "ACME Corporation")')
        parser.add_argument('schema', type=str, help='Schema name - letters, numbers, underscore only (e.g., "acme")')
        parser.add_argument('--domain', type=str, help='Domain (defaults to {schema}.localhost for dev)')
        parser.add_argument('--production', action='store_true', help='Production mode - requires explicit domain')

    def handle(self, *args, **options):
        schema_name = options['schema'].lower()
        
        # Validate schema name
        if not schema_name.replace('_', '').isalnum():
            self.stdout.write(
                self.style.ERROR('Schema name must contain only letters, numbers, and underscores')
            )
            return
        
        # Determine domain
        if options['production'] and not options['domain']:
            self.stdout.write(
                self.style.ERROR('Production mode requires explicit --domain parameter')
            )
            return
        
        domain_name = options['domain'] or f"{schema_name}.localhost"
        
        try:
            with transaction.atomic():
                # Check if tenant or domain already exists
                if Tenant.objects.filter(schema_name=schema_name).exists():
                    self.stdout.write(
                        self.style.ERROR(f'Tenant with schema "{schema_name}" already exists')
                    )
                    return
                
                if Domain.objects.filter(domain=domain_name).exists():
                    self.stdout.write(
                        self.style.ERROR(f'Domain "{domain_name}" already exists')
                    )
                    return
                
                # Create tenant
                tenant = Tenant.objects.create(
                    name=options['name'],
                    schema_name=schema_name,
                    contact_email=f'admin@{domain_name}'
                )
                
                # Create domain
                domain = Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully created tenant:\n'
                        f'   Name: {tenant.name}\n'
                        f'   Schema: {tenant.schema_name}\n' 
                        f'   Domain: {domain.domain}\n'
                        f'   Access URL: http://{domain.domain}:8000/'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating tenant: {e}')
            )
