from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Clean up tenant permissions - remove platform-level permissions'

    def handle(self, *args, **options):
        from django.db import connection
        schema_name = connection.schema_name
        
        self.stdout.write(f'🧹 Cleaning permissions in {schema_name} schema')
        
        # Define permissions that should NOT exist in tenant schemas
        forbidden_apps = [
            'admin',           # Django admin logs - platform only
            'platform',        # Platform super users - platform only  
            'tenants',         # Tenant management - platform only
            'demo',            # Demo requests - public schema only
            'token_blacklist', # JWT token management - platform only
            'sessions',        # Session management - not for tenant users
        ]
        
        # Define forbidden permission types for remaining apps
        forbidden_codenames = [
            # Core Django permissions that tenant users shouldn't have
            'add_permission', 'change_permission', 'delete_permission',
            'add_contenttype', 'change_contenttype', 'delete_contenttype',
            'add_session', 'change_session', 'delete_session',
        ]
        
        # Remove permissions for forbidden apps
        for app_label in forbidden_apps:
            deleted_count = Permission.objects.filter(
                content_type__app_label=app_label
            ).delete()[0]
            
            if deleted_count > 0:
                self.stdout.write(f'❌ Removed {deleted_count} {app_label} permissions')
        
        # Remove specific forbidden permissions
        deleted_count = Permission.objects.filter(
            codename__in=forbidden_codenames
        ).delete()[0]
        
        if deleted_count > 0:
            self.stdout.write(f'❌ Removed {deleted_count} core Django permissions')
        
        # Show remaining permissions
        remaining_perms = Permission.objects.all().order_by('content_type__app_label', 'codename')
        
        self.stdout.write(f'\n✅ Remaining permissions in {schema_name}:')
        current_app = None
        for perm in remaining_perms:
            if current_app != perm.content_type.app_label:
                current_app = perm.content_type.app_label
                self.stdout.write(f'\n📦 {current_app.upper()}:')
            
            self.stdout.write(f'  - {perm.codename} ({perm.name})')
        
        self.stdout.write(f'\n📊 Total remaining permissions: {remaining_perms.count()}')
        self.stdout.write(self.style.SUCCESS(f'🎉 Permission cleanup complete for {schema_name}!'))
