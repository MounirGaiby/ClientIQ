from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create the public tenant for Django admin access'

    def handle(self, *args, **options):
        # Create public tenant (required for django-tenants admin access)
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public Schema',
                'contact_email': 'admin@localhost',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created public tenant')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Public tenant already exists')
            )

        # Create domains for admin access
        domains_to_create = [
            'localhost',
            '127.0.0.1',
            'localhost:8000',
            '127.0.0.1:8000',
        ]
        
        for domain_name in domains_to_create:
            domain, created = Domain.objects.get_or_create(
                domain=domain_name,
                defaults={'tenant': public_tenant, 'is_primary': True}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created domain: {domain_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Domain already exists: {domain_name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Public tenant setup complete! Django admin should now be accessible.')
        )
